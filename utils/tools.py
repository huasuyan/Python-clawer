def merge_unique_news(new_items_list, unique_key="url"):
    """
    合并多个新闻列表，全局去重
    自动兼容嵌套列表，彻底解决 'list' object has no attribute 'get'
    """
    result = []
    seen = set()

    for lst in new_items_list:
        # 如果里面还是列表，自动再遍历一层
        if isinstance(lst, list) and len(lst) > 0 and isinstance(lst[0], list):
            lst = lst[0]

        for news in lst:
            # 安全判断：必须是字典才能 get
            if not isinstance(news, dict):
                continue

            key = news.get(unique_key)
            if key and key not in seen:
                seen.add(key)
                result.append(news)

    return result


def list_intersect(lists, unique_key="url"):
    """
    传入 N 个列表，返回它们的交集（按 unique_key）
    自动处理嵌套列表，彻底解决 get() 报错
    """
    if not lists:
        return []

    # 自动展开所有嵌套的列表
    def flat_items(lst):
        flat = []
        for item in lst:
            if isinstance(item, list):
                flat.extend(item)
            else:
                flat.append(item)
        return flat

    # 第一步：把每个列表展开，并提取 unique_key 集合
    key_sets = []
    for lst in lists:
        flat = flat_items(lst)
        keys = set()
        for item in flat:
            if isinstance(item, dict):
                key = item.get(unique_key)
                if key is not None:
                    keys.add(key)
        key_sets.append(keys)

    # 第二步：求所有列表的共同 key
    common_keys = set.intersection(*key_sets)

    # 第三步：从第一个列表取出共同 key 对应的项
    result = []
    seen = set()
    first_flat = flat_items(lists[0])
    for item in first_flat:
        if not isinstance(item, dict):
            continue
        key = item.get(unique_key)
        if key in common_keys and key not in seen:
            seen.add(key)
            result.append(item)

    return result