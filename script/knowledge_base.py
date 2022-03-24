ActionMap = {'pickup': 'PickupObject',
             'cut': 'SliceObject',
             'place': 'PutObject',
             }

# List of involved objects
OBJECT_LIST = ['Bread', 'Toaster', 'Knife', 'Apple', 'Lettuce', 'Potato',
               'Tomato', 'SinkBasin', 'Bowl', 'Cup', 'Mug', 'Pan',
               'Plate', 'Pot', 'Microwave', 'Egg', 'Book', 'Bottle',
               'Cellphone', 'Sponge', 'Fork', 'Kettle', 'Ladle', 'Tissue',
               'Pen', 'Pencil', 'Pepper', 'Salt', 'Soap', 'Spatula',
               'Spoon', 'Wine', 'Faucet', 'StoveKnob']

DELIVERY_OBJECT_LIST = ['Apple', 'Book', 'Bottle', 'Bowl', 'Bread', 'Cellphone',
                        'Cup', 'Egg', 'Fork', 'Kettle', 'Knife', 'Ladle', 'Lettuce',
                        'Mug', 'Pan', 'Pen', 'Pencil', 'Plate', 'Pot', 'Potato',
                        'Spatula', 'Spoon', 'Tomato', 'Wine']

CUT_OBJECT_ATTRIBUTES = {'Tomato': 'CUTTABLE', 'Apple': 'CUTTABLE', 'Bread': 'CUTTABLE',
                         'Lettuce': 'CUTTABLE', 'Potato': 'CUTTABLE',  'Knife': 'CUTTOOL'}

PNP_OBJECT_ATTRIBUTES = {'Tomato': 'GRASPABLE', 'Apple': 'GRASPABLE', 'Bread': 'GRASPABLE',
                         'Egg': 'GRASPABLE', 'Lettuce': 'GRASPABLE', 'Potato': 'GRASPABLE',
                         'Plate': 'CONTAINABLE', 'Pan': 'CONTAINABLE', 'Pot': 'CONTAINABLE',
                         'Bowl': 'CONTAINABLE'}

OD_OBJECT_ATTRIBUTES = {}

for obj in OBJECT_LIST:
    if obj not in CUT_OBJECT_ATTRIBUTES:
        CUT_OBJECT_ATTRIBUTES[obj] = 'NOATTRIBUTES'

    if obj not in PNP_OBJECT_ATTRIBUTES:
        PNP_OBJECT_ATTRIBUTES[obj] = 'NOATTRIBUTES'

    if obj not in DELIVERY_OBJECT_LIST:
        OD_OBJECT_ATTRIBUTES[obj] = 'NOATTRIBUTES'
    else:
        OD_OBJECT_ATTRIBUTES[obj] = 'GRASPABLE'