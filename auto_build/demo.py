import os

lst = []


# 找出目标文件
def get_if_dir(file_path, tar_file_name):
    temp_list = os.listdir(file_path)
    for temp in temp_list:
        path = file_path + '\\' + temp
        a = os.path.split(path)[-1]
        print("a::::::::", a)
        if os.path.isfile(path):
            if tar_file_name == os.path.split(path)[-1]:
                lst.append(path)
            else:
                continue
        else:
            get_if_dir(path, tar_file_name)


if __name__ == '__main__':
    get_if_dir(file_path='E:/xjToolingBasic', tar_file_name='tooling-basic.jar')
    print(lst)
