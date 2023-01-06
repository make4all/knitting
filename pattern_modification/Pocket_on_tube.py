import itertools
# given object param
max_course = 20
# Add pockets on the back layer, so we set target_layer = 'b'
current_course = 0
# pocket param
pocket_start_course = 5
pocket_end_course = 10
pocket_start_column = 10
pocket_end_column = 20
pocket_height = pocket_end_course - pocket_start_course 
pocket_width = pocket_end_column - pocket_start_column
layer_order = [1, 2]
iter_layer = itertools.cycle(layer_order)
layer_knit_dir_order = ['+', '-']
iter_layer_knit_dir_order = itertools.cycle(layer_knit_dir_order)
layer_bed_order = ['f', 'b']
iter_layer_bed = itertools.cycle(layer_bed_order)
layer_to_add_pocket_on = 2
pocket_layer = 3 
layer_to_bed = {1:'f', 2:'b'}
#note that to avoid wrangling and also to fabricate pocket with least number of xfer, pocket_layer should always be added 
# to the immediately following order. For example, if
# the layer_to_add_pocket_on is 2, then layer order should be updated to [1,2,3] for the pocket adding area; if layer_to_add_pocket_on
# is 1, then layer order should be updated to [1,3,2] for the pocket adding area.
pocket_layer_bed = layer_bed_order[layer_order.index(layer_to_add_pocket_on)]
pocket_layer_knit_dir = ['-', '+']
iter_pocket_layer_knit_dir = itertools.cycle(pocket_layer_knit_dir)
next_layer = next(iter_layer) 
next_layer_knit_dir = next(iter_layer_knit_dir_order)
next_layer_bed = next(iter_layer_bed)
next_pocket_layer_knit_dir = next(iter_pocket_layer_knit_dir)
layers_on_front_bed = set()
layers_on_back_bed = set()
def add_layers_on_bed(current_layer, bed):
    if bed == 'f':
        layers_on_front_bed.add(current_layer)
    elif bed == 'b':
        layers_on_back_bed.add(current_layer)
# if xfer happens, delete() is activated
def delete_layers_on_bed(current_layer, bed):
    if bed == 'f':
        layers_on_front_bed.remove(current_layer)
    elif bed == 'b':
        layers_on_back_bed.remove(current_layer)
# 
def get_num_of_layers_on_bed(bed):
    return len(layers_on_front_bed) if bed == 'f' else len(layers_on_back_bed)
# 
def get_layers_on_bed(bed):
    return layers_on_front_bed if bed == 'f' else layers_on_back_bed
# 
def get_opposite_bed(bed):
    return 'f' if bed == 'b' else 'b'
# 
def get_bed_of_layer(layer):
    if layer in layers_on_front_bed and layer in layers_on_back_bed:
        raise Exception("layer can't appear in both beds!")
    if layer in layers_on_front_bed:
        return 'f'
    elif layer in layers_on_back_bed:
        return 'b'
#
def bed_layer_match(layer):
    curr_bed = get_bed_of_layer(layer)    
    if layer_to_bed[layer] == curr_bed:
        return True
    else:
        return False

while current_course < max_course:
    if current_course < pocket_start_course:
        layer_count = len(layer_order)
        while layer_count > 0:
            # knit next_layer on next_layer_bed with next_layer_knit_dir
            print(f'knit {next_layer} on {next_layer_bed} with {next_layer_knit_dir} direction')
            current_layer = next_layer
            current_layer_bed = next_layer_bed
            add_layers_on_bed(current_layer, bed = current_layer_bed)
            next_layer = next(iter_layer) 
            next_layer_knit_dir = next(iter_layer_knit_dir_order)
            next_layer_bed = next(iter_layer_bed)
            layer_count -= 1
    elif pocket_start_course <= current_course <= pocket_end_course:
        if current_course == pocket_start_course:
            layer_order.insert(layer_order.index(layer_to_add_pocket_on)+1, pocket_layer)
            layer_bed_order.insert(layer_order.index(layer_to_add_pocket_on)+1, pocket_layer_bed)
            iter_layer = itertools.cycle(layer_order)
            iter_layer_knit_dir_order = itertools.cycle(layer_knit_dir_order)
            iter_layer_bed = itertools.cycle(layer_bed_order)
            next_layer = next(iter_layer) 
            next_layer_bed = next(iter_layer_bed)
            next_layer_knit_dir = next(iter_layer_knit_dir_order)
            print(f'layer_order is {layer_order},layer_bed_order is {layer_bed_order}')
        layer_count = len(layer_order)
#         next_layer = next(iter_layer) 
#         print(f'next_layer is {next_layer}')
        while layer_count > 0:
            if next_layer == layer_to_add_pocket_on:
                # xfer loops on the next_layer_bed to the opposite_bed 
                print(f'xfer {next_layer} from {next_layer_bed} to {get_opposite_bed(next_layer_bed)}') 
                delete_layers_on_bed(next_layer, bed = next_layer_bed)
                next_layer_bed = get_opposite_bed(next_layer_bed) #because we xfer above
                if current_course == pocket_start_course:
                    # knit next_layer on next_layer_bed for column not in range[pocket_start_column, pocket_end_column] else split
                    print(f'knit {next_layer} on {next_layer_bed} for column not in range[pocket_start_column, pocket_end_column] else split with {next_layer_knit_dir} direction') 
                else:
                    # knit next_layer on next_layer_bed for column not in [pocket_start_column, pocket_end_column] else split
                    print(f'knit {next_layer} on {next_layer_bed} for column not in [pocket_start_column, pocket_end_column] else split with {next_layer_knit_dir} direction')
                current_layer = next_layer
                current_layer_bed = next_layer_bed
                add_layers_on_bed(current_layer, bed = current_layer_bed)
                next_layer = next(iter_layer) 
                next_layer_bed = next(iter_layer_bed)
#                 print(f'h1 next_layer is {next_layer}')
                # below is because we need to knit the pocket layer once we knit the layer_to_add_pocket_on
                next_layer_knit_dir = next(iter_pocket_layer_knit_dir)
            elif next_layer == pocket_layer:
                # knit next_layer on pocket_layer_bed with next_layer_knit_dir
                print(f'knit pocket_layer {next_layer} on {pocket_layer_bed} with {next_layer_knit_dir} direction')
                current_layer = next_layer
                current_layer_bed = pocket_layer_bed
                add_layers_on_bed(current_layer, bed = current_layer_bed)
                next_layer = next(iter_layer) 
                next_layer_bed = next(iter_layer_bed)
                next_layer_knit_dir = next(iter_layer_knit_dir_order)
#                 print(f'h2 next_layer is {next_layer}')
            else:
                if get_num_of_layers_on_bed(next_layer_bed) > 1:
                    # xfer layers that are not next_layer on the next_layer_bed to the opposite_bed  
#                     layers_on_bed = get_layers_on_bed(next_layer_bed)
#                     print(f'layers_on_bed is {layers_on_bed}')
                    for layer in get_layers_on_bed(next_layer_bed).copy():
                        if layer != next_layer:
                            print(f'xfer {layer} from {next_layer_bed} to {get_opposite_bed(next_layer_bed)}')
                            delete_layers_on_bed(layer, bed = next_layer_bed)
                            add_layers_on_bed(layer, bed = get_opposite_bed(next_layer_bed))
                # knit next_layer on next_layer_bed with next_layer_knit_dir
                print(f'knit {next_layer} on {next_layer_bed} with {next_layer_knit_dir} direction')
                current_layer = next_layer
                current_layer_bed = next_layer_bed
                add_layers_on_bed(current_layer, bed = current_layer_bed)
                next_layer = next(iter_layer) 
                next_layer_bed = next(iter_layer_bed)
                next_layer_knit_dir = next(iter_layer_knit_dir_order)
#                 print(f'h3 next_layer is {next_layer}')
            layer_count -= 1
    else:
        if current_course == pocket_end_course + 1:
            layer_order.remove(pocket_layer)
            layer_bed_order.remove(pocket_layer_bed)
            delete_layers_on_bed(pocket_layer, bed = pocket_layer_bed)
            iter_layer = itertools.cycle(layer_order)
            iter_layer_knit_dir_order = itertools.cycle(layer_knit_dir_order)
            iter_layer_bed = itertools.cycle(layer_bed_order)
            next_layer = next(iter_layer) 
            next_layer_bed = next(iter_layer_bed)
            next_layer_knit_dir = next(iter_layer_knit_dir_order)
        layer_count = len(layer_order)
        while layer_count > 0:
            if bed_layer_match(next_layer) == False:
                print(f'xfer layer {next_layer} from {get_bed_of_layer(next_layer)} to {get_opposite_bed(get_bed_of_layer(next_layer))}')
                delete_layers_on_bed(next_layer, get_bed_of_layer(next_layer))
            # knit next_layer on next_layer_bed with next_layer_knit_dir
            print(f'knit {next_layer} on {next_layer_bed} with {next_layer_knit_dir} direction')
            current_layer = next_layer
            current_layer_bed = next_layer_bed
            add_layers_on_bed(current_layer, bed = current_layer_bed)
            next_layer = next(iter_layer) 
            next_layer_bed = next(iter_layer_bed)
            next_layer_knit_dir = next(iter_layer_knit_dir_order)
            layer_count -= 1
    current_course += 1
