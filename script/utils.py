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

def check_if_object_in_sink(controller, gt_object_infos, gt_subject_infos):
    if gt_object_infos is None or gt_subject_infos is None:
        return False

    for gt_obj in gt_object_infos:
        gt_obj_mask = controller.last_event.instance_masks[gt_obj['objectId']]
        for gt_subject in gt_subject_infos:
            gt_subject_mask = controller.last_event.instance_masks[gt_subject['objectId']]

            if np.sum(np.logical_and(gt_obj_mask, gt_subject_mask)) / np.sum(gt_obj_mask) > 0.8:
                return True

    return False

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

def get_groundtruth_perception_cook(controller, scene_info, cook_object_type, OBJECT_LIST, OBJECT_ATTRIBUTES):
    gt_object = gt_object_info = None
    gt_subject = gt_subject_info = None

    if cook_object_type == 'Pan':
        gt_knob_info = getObjectInfo(controller, 'StoveKnob')

    for obj in scene_info['objects']:
        object_type = obj['type']
        if object_type not in OBJECT_LIST:
            continue
        if OBJECT_ATTRIBUTES[object_type] == 'COOKOBJECT' and obj['is_goal_object']:
            gt_subject = object_type
            if cook_object_type == 'Toaster' and gt_subject == "Bread":
                gt_subject_info = getBreadSeg(controller)
            else:
                gt_subject_info = getObjectSeg(controller, gt_subject)
        elif OBJECT_ATTRIBUTES[object_type] == 'COOKTOOL' and obj['is_goal_object']:
            gt_object = object_type
            gt_object_info = getObjectInfo(controller, gt_object)

    if cook_object_type == 'Pan':
        return gt_knob_info, gt_object, gt_object_info, gt_subject, gt_subject_info
    else:
        return gt_object, gt_object_info, gt_subject, gt_subject_info

def get_groundtruth_perception_od(controller, scene_info, OBJECT_LIST, OBJECT_ATTRIBUTES):
    gt_subject = gt_subject_info = None
    for obj in scene_info['objects']:
        object_type = obj['type']
        if object_type not in OBJECT_LIST:
            continue
        if OBJECT_ATTRIBUTES[object_type] == 'GRASPABLE' and obj['is_goal_object']:
            gt_subject = object_type
            gt_subject_info = getObjectInfo(controller, gt_subject)

    return gt_subject, gt_subject_info

def get_groundtruth_perception_pnp(controller, scene_info, OBJECT_LIST, OBJECT_ATTRIBUTES):
    gt_object = gt_object_info = None
    gt_subject = gt_subject_info = None
    for obj in scene_info['objects']:
        object_type = obj['type']
        if object_type not in OBJECT_LIST:
            continue
        if OBJECT_ATTRIBUTES[object_type] == 'GRASPABLE' and obj['is_goal_object']:
            gt_subject = object_type
            # gt_subject_seg = getObjectSeg(controller, gt_subject)
            gt_subject_info = getObjectInfo(controller, gt_subject)
        elif OBJECT_ATTRIBUTES[object_type] == 'CONTAINABLE' and obj['is_goal_object']:
            gt_object = object_type
            # gt_object_seg = getObjectSeg(controller, gt_object)
            gt_object_info = getObjectInfo(controller, gt_object)

    return gt_object, gt_object_info, gt_subject, gt_subject_info

def get_groundtruth_perception_cut(controller, scene_info, OBJECT_LIST, OBJECT_ATTRIBUTES):
    gt_object = gt_object_info = None
    gt_subject = gt_subject_info = None
    for obj in scene_info['objects']:
        object_type = obj['type']
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

def get_groundtruth_perception_clean(controller, scene_info, OBJECT_LIST, OBJECT_ATTRIBUTES):
    gt_object = gt_object_info = None
    gt_subject = gt_subject_info = None
    gt_faucet = gt_faucet_info = None
    for obj in scene_info['objects']:
        object_type = obj['type']
        if object_type == 'Sink':
            object_type = 'SinkBasin'
        if object_type not in OBJECT_LIST:
            continue
        if OBJECT_ATTRIBUTES[object_type] == 'GRASPABLE' and obj['is_goal_object']:
            gt_subject = object_type
            gt_subject_info = getObjectInfo(controller, gt_subject)
        elif OBJECT_ATTRIBUTES[object_type] == 'CONTAINABLE' and obj['is_goal_object']:
            gt_object = object_type
            gt_object_info = getObjectInfo(controller, gt_object)
        elif OBJECT_ATTRIBUTES[object_type] == 'TOGGLEABLE' and obj['is_goal_object']:
            gt_faucet = object_type
            gt_faucet_info = getObjectInfo(controller, gt_faucet)

    return gt_object, gt_object_info, gt_subject, gt_subject_info, gt_faucet, gt_faucet_info

def construct_initial_state(labels, gt_object, gt_subject, prediction, OBJECT_LIST, OBJECT_ATTRIBUTES):
    init_state = ''
    objects = ''
    unique_object_list = []

    pred_object_seg = []
    pred_subject_seg = []
    object = None
    subject = None

    for i, label in enumerate(labels):
        if OBJECT_LIST[label - 1] not in unique_object_list:
            init_state += ' ('
            init_state += OBJECT_ATTRIBUTES[OBJECT_LIST[label - 1]]
            init_state += ' '
            init_state += OBJECT_LIST[label - 1]
            init_state += ')'
            objects += ' '
            objects += OBJECT_LIST[label - 1]
            unique_object_list.append(OBJECT_LIST[label - 1])

        # the label is ordered by the confidence score, thus the first one is the most confident one
        if gt_object is not None and OBJECT_LIST[label - 1] == gt_object:
            object = OBJECT_LIST[label - 1]
            mask = prediction[0]['masks'][i].cpu().numpy()
            mask = mask[0]
            # mask = mask > args.maskrcnn_score_thre
            pred_object_seg.append(mask)

        if gt_subject is not None and OBJECT_LIST[label - 1] == gt_subject:
            subject = OBJECT_LIST[label - 1]
            mask = prediction[0]['masks'][i].cpu().numpy()
            mask = mask[0]
            # mask = mask > args.maskrcnn_score_thre
            pred_subject_seg.append(mask)

    if gt_object is None:
        return init_state, objects, subject, pred_subject_seg
    elif gt_subject is None:
        return init_state, objects, object, pred_object_seg
    else:
        return init_state, objects, object, pred_object_seg, subject, pred_subject_seg

def construct_initial_state_clean(labels, gt_object, gt_subject, gt_faucet, prediction, OBJECT_LIST, OBJECT_ATTRIBUTES):
    init_state = ''
    objects = ''
    unique_object_list = []

    pred_object_seg = []
    pred_subject_seg = []
    pred_faucet_seg = []
    object = None
    subject = None
    faucet = None

    for i, label in enumerate(labels):
        if OBJECT_LIST[label - 1] not in unique_object_list:
            init_state += ' ('
            init_state += OBJECT_ATTRIBUTES[OBJECT_LIST[label - 1]]
            init_state += ' '
            objects += ' '

        if (OBJECT_LIST[label - 1] == 'SinkBasin'):
            init_state += 'Sink'
            init_state += ')'
            objects += 'Sink'
            unique_object_list.append('Sink')
        else:
            init_state += OBJECT_LIST[label - 1]
            init_state += ')'
            objects += OBJECT_LIST[label - 1]
            unique_object_list.append(OBJECT_LIST[label - 1])

        # the label is ordered by the confidence score, thus the first one is the most confident one
        if gt_object is not None and OBJECT_LIST[label - 1] == gt_object:
            object = OBJECT_LIST[label - 1]
            mask = prediction[0]['masks'][i].cpu().numpy()
            mask = mask[0]
            # mask = mask > args.maskrcnn_score_thre
            pred_object_seg.append(mask)

        if gt_subject is not None and OBJECT_LIST[label - 1] == gt_subject:
            subject = OBJECT_LIST[label - 1]
            mask = prediction[0]['masks'][i].cpu().numpy()
            mask = mask[0]
            # mask = mask > args.maskrcnn_score_thre
            pred_subject_seg.append(mask)

        if OBJECT_LIST[label - 1] == gt_faucet:
            faucet = OBJECT_LIST[label - 1]
            mask = prediction[0]['masks'][i].cpu().numpy()
            mask = mask[0]
            # mask = mask > args.maskrcnn_score_thre
            pred_faucet_seg.append(mask)

    return init_state, objects, object, pred_object_seg, subject, pred_subject_seg, faucet, pred_faucet_seg

def construct_initial_state_cook(labels, gt_object, gt_subject, cook_object_type, prediction,
                                 OBJECT_LIST, COOKABLE_OBJECT_ATTRIBUTES, COOK_TOOL_ATTRIBUTES):
    init_state = ''
    objects = ''
    unique_object_list = []

    pred_object_seg = []
    pred_subject_seg = []
    pred_knob_seg = []
    object = None
    subject = None

    for i, label in enumerate(labels):
        if OBJECT_LIST[label - 1] not in unique_object_list:
            objects += ' '
            objects += OBJECT_LIST[label - 1]
            unique_object_list.append(OBJECT_LIST[label - 1])

        if OBJECT_LIST[label - 1] == gt_object:
            object = OBJECT_LIST[label - 1]
            mask = prediction[0]['masks'][i].cpu().numpy()
            mask = mask[0]
            pred_object_seg.append(mask)
            # mask = mask > args.maskrcnn_score_thre
            for attr in COOK_TOOL_ATTRIBUTES[object]:
                init_state += ' ('
                init_state += attr
                init_state += ' '
                init_state += object
                init_state += ')'

        if OBJECT_LIST[label - 1] == gt_subject:
            subject = OBJECT_LIST[label - 1]
            mask = prediction[0]['masks'][i].cpu().numpy()
            mask = mask[0]
            # mask = mask > args.maskrcnn_score_thre
            for attr in COOKABLE_OBJECT_ATTRIBUTES[subject]:
                init_state += ' ('
                init_state += attr
                init_state += ' '
                init_state += subject
                init_state += ')'
            pred_subject_seg.append(mask)

        if cook_object_type == 'Pan' and (OBJECT_LIST[label - 1] == 'StoveKnob'):
            mask = prediction[0]['masks'][i].cpu().numpy()
            mask = mask[0]
            # mask = mask > args.maskrcnn_score_thre
            pred_knob_seg.append(mask)

    if cook_object_type == 'Pan':
        return init_state, objects, object, pred_object_seg, subject, pred_subject_seg, pred_knob_seg
    else:
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

    return pos

def target_bread_select(depth_image, gt_obj_infos, pred_obj_masks, threshold):
    best_score_bread = float('-inf')
    selected_bread = None
    # select the best bread
    for pred_obj_mask in pred_obj_masks:
        pred_obj_mask_bool = pred_obj_mask > threshold
        # firstly check if this mask has 50% IoU with any ground-truth mask
        for gt_obj_name in gt_obj_infos:
            gt_mask_bool = gt_obj_infos[gt_obj_name]['mask']
            # gt_mask_bool = gt_mask > threshold
            if np.sum(np.logical_and(pred_obj_mask_bool, gt_mask_bool)) / np.sum(gt_mask_bool) < 0.5:
                break

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
            if score > best_score_bread:
                best_score_bread = score
                selected_bread = gt_obj_infos[gt_obj_name]['individual']

    # select the closest bread slice
    target_obj_id = ''
    best_depth = float('-inf')
    for objectId, mask in selected_bread:
        ys, xs = np.where(mask)
        y, x = int(np.mean(ys)), int(np.mean(xs))
        depth = depth_image[y, x]
        depth_min = np.min(depth_image)
        depth_max = np.max(depth_image)
        depth_score = (depth - depth_min) / (depth_max - depth_min)
        if depth_score > best_depth:
            best_depth = depth_score
            target_obj_id = objectId

    return target_obj_id

def getBreadSeg(controller):
    objects_info = {}
    for obj in controller.last_event.metadata['objects']:
        if obj['objectType'] == 'Bread' or obj['objectType'] == 'BreadSliced':
            if obj['objectId'] not in controller.last_event.instance_masks:
                continue

            name = obj['name'].split('_')
            name = '_'.join(name[:2])

            if name not in objects_info:
                objects_info[name] = {}
                mask = controller.last_event.instance_masks[obj['objectId']]
                objects_info[name]['mask'] = mask
                objects_info[name]['individual'] = [(obj['objectId'], mask)]
            else:
                mask = controller.last_event.instance_masks[obj['objectId']]
                objects_info[name]['mask'] = np.logical_or(objects_info[name]['mask'], mask)
                objects_info[name]['individual'].append((obj['objectId'], mask))

    return objects_info

# def getBreadSeg(controller, object):
#     assert object == 'Bread'
#     object_seg = {}
#     for obj, mask in controller.last_event.instance_masks.items():
#         if (obj.find(object) != -1):
#             pos = find_all_substring(obj, object)
#             assert len(pos) == 2
#             obj_id = obj[:pos[1]]
#             if obj_id not in object_seg:
#                 object_seg[obj_id] = mask
#             else:
#                 object_seg[obj_id] = np.logical_or(object_seg[obj_id], mask)
#     return list(object_seg.values())

def dirty(controller, obj_type):
    for o in controller.last_event.metadata["objects"]:
        if o["objectType"] == obj_type:
            _ = controller.step(
                action="DirtyObject",
                objectId=o['objectId'],
                forceAction=True
            )