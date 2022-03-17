ActionMap = {'pickup': 'PickupObject',
             'cut': 'SliceObject',
             }

# List of involved objects
OBJECT_LIST = ['Bread', 'Toaster', 'Knife', 'Apple', 'Lettuce', 'Potato',
               'Tomato', 'SinkBasin', 'Bowl', 'Cup', 'Mug', 'Pan',
               'Plate', 'Pot', 'Microwave', 'Egg', 'Book', 'Bottle',
               'Cellphone', 'Sponge', 'Fork', 'Kettle', 'Ladle', 'Tissue',
               'Pen', 'Pencil', 'Pepper', 'Salt', 'Soap', 'Spatula',
               'Spoon', 'Wine', 'Faucet', 'StoveKnob']

OBJECT_ATTRIBUTES = {'Tomato': 'CUTTABLE', 'Apple': 'CUTTABLE', 'Bread': 'CUTTABLE',
                     'Lettuce': 'CUTTABLE', 'Potato': 'CUTTABLE',  'Knife': 'CUTTOOL'}

for obj in OBJECT_LIST:
    if obj not in OBJECT_ATTRIBUTES:
        OBJECT_ATTRIBUTES[obj] = 'NOATTRIBUTES'