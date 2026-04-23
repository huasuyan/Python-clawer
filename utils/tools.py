def merge_unique_news(new_items_list, unique_key="url"):
    """
    合并多个新闻列表，全局去重
    """
    result = []
    seen = set()
    print(f"\n[合并去重] 去重键: {unique_key}")

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

    print(f"[合并去重] 完成 | 原始总数: {len([n for lst in new_items_list for n in lst])} | 去重后: {len(result)}")
    return result


def list_intersect(lists, unique_key="url"):
    """
    传入 N 个列表，返回它们的交集（按 unique_key）
    """
    if not lists:
        print("[调试] lists 为空，直接返回 []")
        return []

    print(f"[调试] 开始计算交集，unique_key = {unique_key}")
    print(f"[调试] 传入了 {len(lists)} 个列表")

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
    for i, lst in enumerate(lists):
        flat = flat_items(lst)
        keys = set()
        for item in flat:
            if isinstance(item, dict):
                key = item.get(unique_key)
                if key is not None:
                    keys.add(key)
        key_sets.append(keys)
        print(f"[调试] 第 {i+1} 个列表提取到 {len(keys)} 个唯一键")

    # 第二步：求所有列表的共同 key
    common_keys = set.intersection(*key_sets)
    print(f"[调试] 所有列表的共同键数量：{len(common_keys)}")
    if len(common_keys) < 20:
        print(f"[调试] 共同键内容：{common_keys}")

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

    print(f"[调试] 最终返回交集数据 {len(result)} 条")
    return result