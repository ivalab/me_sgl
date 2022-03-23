import os
import pdb
import numpy as np

def construct_result_saving_path(root, task_folder, level_folder, instance_folder):
    save_path = os.path.join(root, task_folder)
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    save_path = os.path.join(save_path, level_folder)
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    save_path = os.path.join(save_path, instance_folder)
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    return save_path

def target_object_select(controller, depth_image, gt_obj_infos, pred_obj_masks, threshold):
    target_obj_id = None

    best_score = float('-inf')
    for pred_obj_mask in pred_obj_masks:
        pred_obj_mask_bool = pred_obj_mask > threshold
        # firstly check if this mask has 50% IoU with any ground-truth mask
        valid = False
        obj_id = None
        for gt_obj in gt_obj_infos:
            gt_mask = controller.last_event.instance_masks[gt_obj['objectId']]
            gt_mask_bool = gt_mask > threshold
            if np.sum(np.logical_and(pred_obj_mask_bool, gt_mask_bool)) / np.sum(gt_mask_bool) >= 0.5:
                valid = True
                obj_id = gt_obj['objectId']
                break

        if not valid:
            continue

        # compute average confidence score
        ys, xs = np.where(pred_obj_mask > threshold)
        conf_score = np.mean(pred_obj_mask[ys, xs])

        # get the depth from camera center to the mean pixel of target object
        y, x = int(np.mean(ys)), int(np.mean(xs))
        depth = depth_image[y, x]
        # normalize the depth to 0 ~ 1
        depth_min = np.min(depth_image)
        depth_max = np.max(depth_image)
        depth_score = (depth - depth_min) / (depth_max - depth_min)

        # weighted sum confidence score and depth score
        score = 0.5 * conf_score + 0.5 * (1 - depth_score)
        if score > best_score:
            best_score = score
            target_obj_id = obj_id

    return target_obj_id

def get_groundtruth_perception(controller, scene_info, OBJECT_LIST, OBJECT_ATTRIBUTES):
    gt_object = gt_object_info = None
    gt_subject = gt_subject_info = None
    scene_objects = []
    for obj in scene_info['objects']:
        object_type = obj['type']
        scene_objects.append(obj['type'])
        if object_type not in OBJECT_LIST:
            continue
        if OBJECT_ATTRIBUTES[object_type] == 'CUTTABLE' and obj['is_goal_object']:
            gt_subject = object_type
            # gt_subject_seg = getObjectSeg(controller, gt_subject)
            gt_subject_info = getObjectInfo(controller, gt_subject)
        elif OBJECT_ATTRIBUTES[object_type] == 'CUTTOOL' and obj['is_goal_object']:
            gt_object = object_type
            # gt_object_seg = getObjectSeg(controller, gt_object)
            gt_object_info = getObjectInfo(controller, gt_object)

    return gt_object, gt_object_info, gt_subject, gt_subject_info
    # return gt_object, gt_object_seg, gt_subject, gt_subject_seg

def construct_initial_state(labels, gt_object, gt_subject, prediction, OBJECT_LIST, OBJECT_ATTRIBUTES):
    init_state = ''
    objects = ''
    unique_object_list = []

    pred_object_seg = []
    pred_subject_seg = []
    object = None
    subject = None

    for i, label in enumerate(labels):
        if (OBJECT_LIST[label - 1] not in unique_object_list):
            init_state += ' ('
            init_state += OBJECT_ATTRIBUTES[OBJECT_LIST[label - 1]]
            init_state += ' '
            init_state += OBJECT_LIST[label - 1]
            init_state += ')'
            objects += ' '
            objects += OBJECT_LIST[label - 1]
            unique_object_list.append(OBJECT_LIST[label - 1])

        # the label is ordered by the confidence score, thus the first one is the most confident one
        if (OBJECT_LIST[label - 1] == gt_object):
            object = OBJECT_LIST[label - 1]
            mask = prediction[0]['masks'][i].cpu().numpy()
            mask = mask[0]
            # mask = mask > args.maskrcnn_score_thre
            pred_object_seg.append(mask)

        if (OBJECT_LIST[label - 1] == gt_subject):
            subject = OBJECT_LIST[label - 1]
            mask = prediction[0]['masks'][i].cpu().numpy()
            mask = mask[0]
            # mask = mask > args.maskrcnn_score_thre
            pred_subject_seg.append(mask)

    return init_state, objects, object, pred_object_seg, subject, pred_subject_seg

def getObjectInfo(controller, object):
    '''
    return all meta information from AI2THOR for certain type of objects
    :param controller: AI2THOR controller
    :param object: string, object tyep
    :return:
    '''
    objects_info = []
    for obj in controller.last_event.metadata["objects"]:
        if obj['objectType'] == object:
            objects_info.append(obj)

    return objects_info

def getObjectSeg(controller, object):
    object_segs = []
    try:
        for obj in controller.last_event.metadata["objects"]:
            if obj['objectType'] == object:
                object_segs.append(controller.last_event.instance_masks[obj['objectId']])
    except KeyError:
        for obj, mask in controller.last_event.instance_masks.items():
            idx1 = obj.find('|')
            if idx1 != -1 and obj[:idx1] == object:
                object_segs.append(mask)
    return object_segs

def find_all_substring(str, sub):
    start = 0
    pos = []
    while True:
        start = str.find(sub, start)
        if start == -1: 
            return pos
        pos.append(start)
        start += len(sub) # use start += 1 to find overlapping matches

def getBreadSeg(controller, object):
    assert object == 'Bread'
    object_seg = {}
    for obj, mask in controller.last_event.instance_masks.items():
        if (obj.find(object) != -1):
            pos = find_all_substring(obj, object)
            assert len(pos) == 2
            obj_id = obj[:pos[1]]
            if obj_id not in object_seg:
                object_seg[obj_id] = mask
            else:
                object_seg[obj_id] = np.logical_or(object_seg[obj_id], mask) 
    return list(object_seg.values())