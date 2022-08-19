import os


class JavaToTxt:
    def __init__(self, file_path, txt_name):
        self.file_path = file_path
        self.path_read = []
        self.txt_name = txt_name

    def get_if_dir(self, file_path):
        temp_list = os.listdir(file_path)
        for temp in temp_list:
            path = file_path + '\\' + temp
            if os.path.isfile(path):
                if os.path.splitext(path)[-1] == '.java':
                    self.path_read.append(path)
                else:
                    continue
            else:
                self.get_if_dir(path)

    def writ_to_txt(self):
        for read_path in self.path_read:
            with open(read_path, 'r', encoding='utf-8') as r:
                file_data = r.read()
                with open(self.txt_name, 'a+', encoding='utf-8') as w:
                    w.write('\n' + file_data)

    def run(self):
        self.get_if_dir(self.file_path)
        self.writ_to_txt()


if __name__ == '__main__':
    file_path = r'E:\gitfiles\ems-konka'
    txt_name = 'java_to_txt2.txt'
    jtt = JavaToTxt(file_path, txt_name)
    jtt.run()
    print('path_read:', jtt.path_read)
    print('java_file_num:', len(jtt.path_read))
