import kdtree

def nonmaximalsuppression(tensor, threshold):
    pred_data = tensor.storage()
    offset = tensor.storage_offset()
    stride = int(tensor.stride()[0])
    numel = tensor.numel()
    points = []

    # Corners
    val = pred_data[0 + offset]
    if val >= threshold and val >= pred_data[1 + offset] and val >= pred_data[stride + offset]:
        points.append([0, 0])

    val = pred_data[stride - 1 + offset]
    if val >= threshold and val >= pred_data[stride - 2 + offset] and val >= pred_data[2 * stride - 1 + offset]:
        points.append([stride - 1, 0])
        
    val = pred_data[numel - stride + offset]
    if val > threshold and val >= pred_data[numel - stride + 1 + offset] and val >= pred_data[numel - 2 * stride + offset]:
        points.append([0, stride - 1])

    val = pred_data[numel - 1 + offset]
    if val > threshold and val >= pred_data[numel -2 + offset] and val >= pred_data[numel - 1 - stride + offset]:
        points.append([stride - 1, stride - 1])

    # Top y==0
    for i in range(1,stride-1):
        i += offset
        val = pred_data[i]
        if val >= threshold and val >= pred_data[i-1] and val >= pred_data[i+1] and val >= pred_data[i+stride]:
            points.append([i - offset, 0])

    # Bottom y==stride-1
    for i in range(numel-stride+1,numel-1):
        i += offset
        val = pred_data[i]
        if val >= threshold and val >= pred_data[i-1] and val >= pred_data[i+1] and val >= pred_data[i-stride]:
            points.append([i - numel + stride - offset, stride - 1])

    # Front x==0
    for i in range(stride, stride * (stride - 1), stride):
        i += offset
        val = pred_data[i]
        if val >= threshold and val >= pred_data[i+stride] and val >= pred_data[i-stride] and val >= pred_data[i+1]:
            points.append([0, (i - offset) // stride])

    # Back x == stride-1
    for i in range(stride - 1, stride * (stride - 1), stride):
        i += offset
        val = pred_data[i]
        if val >= threshold and val >= pred_data[i+stride] and val >= pred_data[i-stride] and val >= pred_data[i-1]:
            points.append([stride - 1, (i - offset) // stride])

    # Remaining inner pixels
    for i in range(stride+1, stride * (stride - 1), stride):
        for j in range(i,i+stride-2):
            j += offset
            val = pred_data[j]
            if val >= threshold and val >= pred_data[j+1] and val >= pred_data[j-1] and val >= pred_data[j+stride] and val >= pred_data[j-stride]:
                points.append([(j - offset) % stride, i // stride])

    return points

def euclid(pt1, pt2):
    return (pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2

def rrtree(lat, threshold):
    if lat is None or len(lat) == 0:
        return []

    tree = kdtree.create(dimensions=2)
    distance_threshold = threshold # 8^2
    for i,pt in enumerate(lat):
        t_pt = (float(pt[0]), float(pt[1]))
        search_result = tree.search_nn(t_pt, dist=euclid)
        if search_result is None:
            tree.add(t_pt)
        else:
            node, dist = search_result[0], search_result[1]
            if dist >= distance_threshold:
                tree.add(t_pt)

    filtered_points = [(int(pt.data[0]), int(pt.data[1])) for pt in kdtree.level_order(tree)]
    return filtered_points
