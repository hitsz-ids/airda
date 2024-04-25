def get_file_extension(filename):
    # 使用split('.')将文件名拆分为文件名和后缀部分
    parts = filename.split(".")

    # 如果文件名中包含多个点，则最后一个点后的部分是后缀
    if len(parts) > 1:
        return parts[-1]
    else:
        # 如果文件名中没有点，或者只有一个点，则没有后缀
        return ""
