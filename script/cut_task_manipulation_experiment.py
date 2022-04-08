import os
import argparse
import subprocess
import json
from PIL import Image

import torch
from torchvision import transforms

from ai2thor.controller import Controller
from knowledge_base import OBJECT_LIST, CUT_OBJECT_ATTRIBUTES, ActionMap
from utils import construct_initial_state, get_groundtruth_perception_cut, \
    target_object_select, construct_result_saving_path

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

def main(args):
    # load pretrained model maskrcnn model
    perception_model = torch.load(args.maskrcnn_model_path)
    perception_model.eval()

    # initialise AI2THOR controller
    controller = Controller(scene="FloorPlan1",
                            width=640,
                            height=480,
                            renderDepthImage=True,
                            renderInstanceSegmentation=True)

    for instance_folder_name in sorted(os.listdir(os.path.join(args.root, args.task_type, args.level))):
        # four evaluation metrics for manipulation experiment
        perception_success = True
        task_learning_success = True
        execution_success = True
        task_planning_success = True

        folder_path = os.path.join(args.root, args.task_type, args.level, instance_folder_name)
        save_path = construct_result_saving_path(args.result_save_root, args.task_type, args.level, instance_folder_name)

        # read scenarios information
        with open(os.path.join(folder_path, 'transformations.json'), 'r') as f:
            scene_info = json.load(f)

        # restore pre-saved environment
        controller.reset(scene=scene_info['scene'])
        controller.step(
            action='SetObjectPoses',
            objectPoses=scene_info['objects'],
            placeStationary=True,
        )
        controller.step(action="Teleport",
                        position=scene_info['agent']['position'],
                        rotation=scene_info['agent']['rotation'],
                        horizon=min(scene_info['agent']['cameraHorizon'], 59.9))
        controller.step(action='Pass')

        # get the ground truth objects and segmentation
        gt_object, gt_object_info, gt_subject, gt_subject_info = get_groundtruth_perception_cut(controller,
                                                                                                scene_info,
                                                                                                OBJECT_LIST,
                                                                                                CUT_OBJECT_ATTRIBUTES)

        # Perception module interprets the scene
        img = Image.fromarray(controller.last_event.frame)  # cv2img)#frame)
        convert_tensor = transforms.ToTensor()
        img = convert_tensor(img)
        with torch.no_grad():
            prediction = perception_model([img.to(device)])

        # Get the object prediction with high confidence
        idx = 0
        for i, score in enumerate(prediction[0]['scores']):
            if score < args.maskrcnn_score_thre:
                break
            idx += 1

        labels = prediction[0]['labels'][:idx].cpu().numpy()

        # construct the initial state of the scene
        init_state, objects, object, pred_object_seg, subject, pred_subject_seg = construct_initial_state(labels,
                                                                                                          gt_object,
                                                                                                          gt_subject,
                                                                                                          prediction,
                                                                                                          OBJECT_LIST,
                                                                                                          CUT_OBJECT_ATTRIBUTES)

        # check if initial state of the scene is constructed successfully
        if subject is None or object is None:
            perception_success = False

        # get the predicted goal state
        with open(os.path.join(save_path, 'pred_pddl_goal_state.txt'), 'r') as f:
            pddl_goal_state_pr = f.readline().split('\n')[0].split()

        # construct PDDL goal state
        pddl_goal_state_written = '(' + pddl_goal_state_pr[0] + ' ' + pddl_goal_state_pr[1] + \
                                  ' ' + pddl_goal_state_pr[2] + ')'

        # get the ground-truth PDDL goal state
        with open(os.path.join(folder_path, 'pddl_goal_state.txt'), 'r') as f:
            pddl_goal_state_gt = f.readline().split('\n')[0].split()

        # check if task learning succeeds
        if pddl_goal_state_pr != pddl_goal_state_gt:
            task_learning_success = False

        # Write PDDL Problem
        objects += ' arm'
        init_state += ' (free arm)'
        pddl_problem = '(define (problem cut_vision)\n' + \
                       '    (:domain cut)\n' + \
                       '    (:objects' + objects + ')\n' + \
                       '    (:init' + init_state + ')\n' + \
                       '    (:goal (and ' + pddl_goal_state_written + '))\n' + \
                       ')\n'

        with open("../PDDL/problem/cut_problem.pddl", "w") as f:
            f.write(pddl_problem)

        # call PDDL solver to solve written problem
        subprocess.call(
            '../downward/fast-downward.py ../PDDL/domain/cut_domain.pddl ../PDDL/problem/cut_problem.pddl '
            '--search "lazy_greedy([ff()], preferred=[ff()])"',
            shell=True) # stdout=subprocess.DEVNULL

        # Parse the plan generated by fast downward into a list of actions and objects
        plan = []
        if os.path.exists('./sas_plan'):
            with open('./sas_plan') as f:
                for i, line in enumerate(f.readlines()[:-1]):
                    action = []
                    # List of words in the current line of the sas_plan
                    elements = line.split('\n')[0]
                    elements = elements[1:-1].split()
                    sub_task = []
                    # action
                    sub_task.append(elements[0])
                    # target object
                    sub_task.append(elements[1])

                    plan.append(sub_task)
            task_planning_success &= perception_success
            task_planning_success &= task_learning_success

            # delete file
            os.remove('./sas_plan')
        else:
            print(f"PDDL doesn't find a solution")
            task_planning_success = False

        execution_success &= task_planning_success

        # perform planned actions
        depth_image = controller.last_event.depth_frame
        ai2thor_action = []
        for sub_task in plan:
            action = sub_task[0]
            target_object = sub_task[1].capitalize()

            # select the object from potential object list
            if target_object == object:
                target_obj_id = target_object_select(controller, depth_image,
                                                     gt_object_info, pred_object_seg, args.maskrcnn_score_thre)
                if target_obj_id is None:
                    execution_success &= False
            elif target_object == subject:
                target_obj_id = target_object_select(controller, depth_image,
                                                     gt_subject_info, pred_subject_seg, args.maskrcnn_score_thre)

                if target_obj_id is None:
                    execution_success &= False

            ai2thor_action.append((action, target_obj_id))

        for action, target_obj_id in ai2thor_action:
            controller.step(
                action=ActionMap[action],
                objectId=target_obj_id,
                forceAction=True
            )
            controller.step(action='Pass')

        # save results for all evaluation metrics
        with open(os.path.join(save_path, 'result.txt'), 'w') as f:
            f.write('Perception module: {}\n'.format(perception_success))
            f.write('Task learning module: {}\n'.format(task_learning_success))
            f.write('Task planning module: {}\n'.format(task_planning_success))
            f.write('Execution module: {}'.format(execution_success))

if __name__ == "__main__":
    # parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=str, default='../data',
                        help='Root folder for saving test samples')
    parser.add_argument('--task_type', type=str, default='cut_task',
                        choices=['cut_task', 'cook_task', 'clean_task', 'object_delivery', 'pick_n_place'],
                        help='Type of manipulation task')
    parser.add_argument('--level', type=str, default='easy', choices=['easy', 'medium', 'hard1'],
                        help='Level of the task, can be easy, median, hard1')
    parser.add_argument('--maskrcnn_model_path', type=str,
                        default='../pretrained_model/maskrcnn_model.pt',
                        help='Path for saved pretrained maskrcnn model')
    parser.add_argument('--maskrcnn_score_thre', type=float, default=0.8,
                        help='Confidence score threshold for maskrcnn detection')
    parser.add_argument('--result_save_root', type=str, default='../result',
                        help='Root folder for saving the result of manipulation experiment')
    args = parser.parse_args()

    main(args)