import os
import argparse
import subprocess
import json
from PIL import Image

import torch
from torchvision import transforms

from ai2thor.controller import Controller
from knowledge_base import OBJECT_LIST, COOK_OBJECT_ATTRIBUTES, \
    COOKABLE_OBJECT_ATTRIBUTES, COOK_TOOL_ATTRIBUTES, ActionMap
from utils import construct_initial_state_cook, get_groundtruth_perception_cook, \
    target_object_select, target_bread_select, construct_result_saving_path

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
        save_path = construct_result_saving_path(args.result_save_root, args.task_type,
                                                 args.level, instance_folder_name)

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
                        horizon=min(scene_info['agent']['rotation']['cameraHorizon'], 59.9))
        cook_object_type = ''
        for obj in scene_info['objects']:
            object_type = obj['type']
            if object_type not in OBJECT_LIST or object_type not in COOK_OBJECT_ATTRIBUTES:
                continue
            elif COOK_OBJECT_ATTRIBUTES[object_type] == 'COOKTOOL' and obj['is_goal_object']:
                cook_object_type = object_type
        # slice the bread
        if cook_object_type == 'Toaster':
            for obj in controller.last_event.metadata["objects"]:
                if obj["objectType"] == 'Bread':
                    _ = controller.step(
                        action="SliceObject",
                        objectId=obj["objectId"],
                        forceAction=True
                    )
        controller.step(action='Pass')

        # get the ground truth objects and segmentation
        if cook_object_type == 'Pan':
            # ToDo: figure out how to extract information for knob
            gt_knob_info, gt_object, gt_object_info, \
            gt_subject, gt_subject_info = get_groundtruth_perception_cook(controller,
                                                                          scene_info,
                                                                          cook_object_type,
                                                                          OBJECT_LIST,
                                                                          COOK_OBJECT_ATTRIBUTES)
        else:
            gt_object, gt_object_info, \
            gt_subject, gt_subject_info = get_groundtruth_perception_cook(controller,
                                                                          scene_info,
                                                                          cook_object_type,
                                                                          OBJECT_LIST,
                                                                          COOK_OBJECT_ATTRIBUTES)

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
        if cook_object_type == 'Pan':
            init_state, objects, object, pred_object_seg, \
            subject, pred_subject_seg, pred_knob_seg = construct_initial_state_cook(labels,
                                                                                    gt_object,
                                                                                    gt_subject,
                                                                                    cook_object_type,
                                                                                    prediction,
                                                                                    OBJECT_LIST,
                                                                                    COOKABLE_OBJECT_ATTRIBUTES,
                                                                                    COOK_TOOL_ATTRIBUTES)
        else:
            init_state, objects, object, pred_object_seg, \
            subject, pred_subject_seg = construct_initial_state_cook(labels,
                                                                     gt_object,
                                                                     gt_subject,
                                                                     cook_object_type,
                                                                     prediction,
                                                                     OBJECT_LIST,
                                                                     COOKABLE_OBJECT_ATTRIBUTES,
                                                                     COOK_TOOL_ATTRIBUTES)

        # check if initial state of the scene is constructed successfully
        if (gt_subject is None and subject is not None) or (gt_subject is not None and subject != gt_subject) or \
                (gt_object is None and object is not None) or \
                (gt_object is not None and object != gt_object):
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
        pddl_problem = '(define (problem cook_vision)\n' + \
                       '    (:domain cook)\n' + \
                       '    (:objects' + objects + ')\n' + \
                       '    (:init' + init_state + ')\n' + \
                       '    (:goal (and ' + pddl_goal_state_written + '))\n' + \
                       ')\n'
        with open("../PDDL/problem/cook_problem.pddl", "w") as f:
            f.write(pddl_problem)

        # call PDDL solver to solve written problem
        subprocess.call(
            '../downward/fast-downward.py ../PDDL/domain/cook_domain.pddl ../PDDL/problem/cook_problem.pddl '
            '--search "lazy_greedy([ff()], preferred=[ff()])"',
            shell=True, stdout=subprocess.DEVNULL)  # stdout=subprocess.DEVNULL

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
                    if elements[0] == 'toggle':
                        sub_task.append(elements[-1])
                    elif elements[0] == 'dropoff':
                        sub_task.append(elements[-1])
                    else:
                        sub_task.append(elements[1])

                    plan.append(sub_task)
            task_planning_success = False

            # delete file
            os.remove('./sas_plan')
        else:
            print(f"PDDL doesn't find a solution")
            task_planning_success = True

        # For the hard2 scenario, we are not supported to perform any actions
        execution_success &= task_planning_success

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
    parser.add_argument('--task_type', type=str, default='cook_task',
                        choices=['cut_task', 'cook_task', 'clean_task', 'object_delivery', 'pick_n_place'],
                        help='Type of manipulation task')
    parser.add_argument('--level', type=str, default='hard2', choices=['hard2'],
                        help='Level of the task, can only be hard2')
    parser.add_argument('--maskrcnn_model_path', type=str,
                        default='../pretrained_model/maskrcnn_model.pt',
                        help='Path for saved pretrained maskrcnn model')
    parser.add_argument('--maskrcnn_score_thre', type=float, default=0.8,
                        help='Confidence score threshold for maskrcnn detection')
    parser.add_argument('--result_save_root', type=str, default='../result',
                        help='Root folder for saving the result of manipulation experiment')
    args = parser.parse_args()

    main(args)