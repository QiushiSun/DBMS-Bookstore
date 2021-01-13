from aip import AipOcr
from be.model import db_conn
from be.model.buyer import Buyer
import sqlalchemy
import os
import cv2
import time
import jieba.analyse as ana

# 定义常量
APP_ID = '14544448'
API_KEY = 'yRZGUXAlCd0c9vQj1kAjBEfY'
SECRET_KEY = 'sc0DKGy7wZ9MeWFGZnbscbRyoDB2IQlj'

# 初始化AipFace对象
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


# 读取图片
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


class OCR(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
    def OCR_pic_cv(self):
        try:
            #获取图片
            saveDir = 'data/'
            '''
            调用电脑摄像头来自动获取图片
            '''
            if not os.path.exists(saveDir):
                os.makedirs(saveDir)
            count = 1  # 图片计数索引
            cap = cv2.VideoCapture(0)
            width, height, w = 640, 480, 360
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            crop_w_start = (width - w) // 2
            crop_h_start = (height - w) // 2
            print('width: ', width)
            print('height: ', height)

            ret, frame = cap.read()  # 获取相框
            frame = frame[crop_h_start:crop_h_start + w, crop_w_start:crop_w_start + w]  # 展示相框
            # frame=cv2.flip(frame,1,dst=None)
            cv2.imshow("capture", frame)
            action = cv2.waitKey(1) & 0xFF
            time.sleep(3)
            cv2.imwrite("%s/%d.jpg" % (saveDir, count), cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA))
            print(u"%s: %d 张图片" % (saveDir, count))
            count += 1
            cap.release()  # 释放摄像头
            cv2.destroyAllWindows()  # 丢弃窗口

            #ocr图片获取图片文字
            path='./data/1.jpg'
            image = get_file_content(path)
            # 调用通用文字识别, 图片为本地图片
            res = client.general(image)

            print(res)

            results = []
            for item in res['words_result']:
                print(item['words'])
                results.append(item['words'])

            print(results)
            b = Buyer()
            result = b.search_many(results)

        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok", result

    def OCR_pic(self, path):
        try:
            print(path)
            image = get_file_content(path)
            # 调用通用文字识别, 图片为本地图片
            res = client.general(image)
            print(res)
            text = []
            for item in res['words_result']:
                print(item['words'])
                text.append(item['words'])
            print(text)
            text_Seg = []
            text_len = len(text)
            doc = ""
            for i in range(0, text_len):
                doc += text[i]
            print(doc)
            sentence_Seg = ana.textrank(doc)
            # sentence_Seg = str(sentence_Seg)
            # sentence_Seg = sentence_Seg.strip(',')
            print(sentence_Seg)

            b = Buyer()
            result = b.search_many(sentence_Seg)


        except sqlalchemy.exc.IntegrityError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok", result

#ocr 结果进行分词，方便检索

# HanLP.Config.ShowTermNature = False
# from pyhanlp import *
# CRFnewSegment = HanLP.newSegment("crf")

# delim = "'\{\”}\[],./'\"(,)<>《》"
#
# def get_ocr_seg_seperated(text): #直接用返回的json进行分词
#     text_Seg = []
#     text_len = len(text)
#     for i in range (0,text_len):
#         temp = CRFnewSegment.seg(text[i])
#         for i in range (0 , len(temp)):
#             if(str(temp[i]) not in delim):
#                 text_Seg.append(str(temp[i]))
#     return text_Seg
#
# def get_ocr_seg_integral(text):  #将返回的结果合并后进行分词
#     text_Seg = []
#     text_len = len(text)
#     doc = ""
#     for i in range(0, text_len):
#         doc += text[i]
#     print(doc)
#     sentence_Seg = CRFnewSegment.seg(doc)
#     sentence_Seg = str(sentence_Seg)
#     sentence_Seg = sentence_Seg.strip(',')
#     print(sentence_Seg)

# test = [
#     "洛",
#     "家信经典",
#     "洛克菲勒",
#     "留给儿子的38封信",
#     "国最省家族世代传的教子经",
#     "n上过本书,可以的",
#     "商和管理才",
#     "中华工商联合出版社"]
# get_ocr_seg_integral(test)