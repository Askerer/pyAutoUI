import pyautogui
import cv2 
from PIL import Image
import numpy as np
import pandas as pd

wh = pyautogui.size()

img = pyautogui.screenshot()

screenshot_array = np.array(img)

# OpenCV 使用的是 BGR 格式，因此需要將 RGB 轉換為 BGR
screenshot_array = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2BGR)

#cv2.imshow('screenshot',screenshot_array)

template = cv2.imread('.\mumu_head.png')

#cv2.imshow('screenshot',img)
# 對模板圖像進行匹配


result = cv2.matchTemplate(screenshot_array, template, cv2.TM_CCOEFF_NORMED)

#print(result)
print(screenshot_array.shape)
print(template.shape)
print(result.shape)

# 將結果數據轉換為 DataFrame
result_df = pd.DataFrame(result)

# 儲存為 CSV 文件
result_df.to_csv('match_template_result.csv', index=False, header=False)

# 獲取匹配結果中的最大值位置
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)


# 設定信心度閾值
threshold = 0.8

# 檢查最大值是否超過閾值
if max_val >= threshold:
    # 確定模板的中心位置
    template_height, template_width = template.shape[:2]
    center_x = max_loc[0] + template_width // 2
    center_y = max_loc[1] + template_height // 2

    # 將滑鼠移動到模板的中心位置
    pyautogui.moveTo(center_x, center_y)

    # 顯示匹配結果（可選）
    cv2.rectangle(screenshot_array, max_loc, (max_loc[0] + template_width, max_loc[1] + template_height), (0, 255, 0), 2)
    cv2.imshow('Matched Image', screenshot_array)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("未找到匹配結果，信心度不足。")


#cv2.waitKey(0)
#cv2.destroyAllWindows()

#print(wh.width)
#print(wh.height)

#pyautogui.moveTo(5,5,0.25)

#pyautogui.moveTo(100,100,0.25)

#pyautogui.mouseInfo()