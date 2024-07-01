def make_array(gateway, klass, list):
    res = gateway.new_array(klass, len(list))
    for i in range(len(list)):
        res[i] = list[i]
    return res
