# ------------------------------------------------------------------------------
# ステップ1: 必要なライブラリのインストールとインポート
# ------------------------------------------------------------------------------
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from PIL import Image

# ------------------------------------------------------------------------------
# ステップ2: Selenium WebDriverのセットアップ
# ------------------------------------------------------------------------------
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu') # VPS環境での安定動作に必須
driver = webdriver.Chrome(options=chrome_options)
print("WebDriverの準備ができました。")

# ------------------------------------------------------------------------------
# ステップ3: Webページ操作とスクリーンショット、そしてトリミング
# ------------------------------------------------------------------------------
url = 'https://www.coinglass.com/FundingRateHeatMap'
full_screenshot_filename = 'heatmap_full.png'
cropped_filename = 'heatmap_cropped.png'
webhook_url = 'https://discord.com/api/webhooks/1405093792683524146/shLGuhQhKQuHh5NFKwgkIx41OM1z7EtGOQMBRe8Wo81AfXbvY5vK6Ev9QkSr2LY74RcV'

try:
    print(f"'{url}' にアクセスしています...")
    driver.get(url)
    driver.set_window_size(1920, 1080)
    wait = WebDriverWait(driver, 30)

    print("ページコンテンツが読み込まれるのを待っています...")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'echarts-for-react')))
    time.sleep(3)

    print("キーボード操作でカラースライダーを一番左に移動します...")
    slider_handle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.ant-slider-handle')))
    slider_handle.click()
    time.sleep(0.5)
    for i in range(100):
        slider_handle.send_keys(Keys.ARROW_LEFT)
    print("スライダーの調整が完了しました。")
    time.sleep(3)

    print("期間を '6 month' に変更します...")
    period_button_xpath = "//button[contains(text(), 'day') or contains(text(), 'month') or contains(text(), 'Year')]"
    period_button = wait.until(EC.element_to_be_clickable((By.XPATH, period_button_xpath)))
    period_button.click()
    time.sleep(1)
    six_month_option_xpath = "//li[text()='6 month']"
    six_month_option = wait.until(EC.element_to_be_clickable((By.XPATH, six_month_option_xpath)))
    six_month_option.click()
    print("期間を '6 month' に変更しました。データを再読み込みしています...")
    time.sleep(10)

    driver.save_screenshot(full_screenshot_filename)
    print(f"フルスクリーンショットを '{full_screenshot_filename}' として保存しました。")

    print("スクリーンショットをトリミングしています...")
    title_element = driver.find_element(By.XPATH, "//h1[text()='Funding Rate Heatmap']")
    period_button_element = driver.find_element(By.XPATH, "//button[contains(text(), '6 month')]")
    heatmap_element = driver.find_element(By.CLASS_NAME, 'echarts-for-react')
    title_loc = title_element.location
    period_loc = period_button_element.location
    period_size = period_button_element.size
    heatmap_loc = heatmap_element.location
    heatmap_size = heatmap_element.size
    padding = 20
    left = title_loc['x'] - padding
    upper = title_loc['y']
    right = period_loc['x'] + period_size['width'] + 2*padding
    lower = heatmap_loc['y'] + heatmap_size['height'] + padding

    img = Image.open(full_screenshot_filename)
    cropped_img = img.crop((left, upper, right, lower))
    cropped_img.save(cropped_filename)
    print(f"トリミングした画像を '{cropped_filename}' として保存しました。")
    
    # --------------------------------------------------------------------------
    # ★★★ ステップ4: Discordへの通知 ★★★
    # --------------------------------------------------------------------------
    print("Discordに画像を送信しています...")
    with open(cropped_filename, 'rb') as f:
        files = {'file': (cropped_filename, f, 'image/png')}
        payload = {'content': '毎朝のFunding Rate Heatmapです。'}
        response = requests.post(webhook_url, data=payload, files=files)
        if response.status_code == 200 or response.status_code == 204:
            print("Discordへの画像送信に成功しました。")
        else:
            print(f"Discordへの送信に失敗しました。ステータスコード: {response.status_code}, レスポンス: {response.text}")

except Exception as e:
    print(f"エラーが発生しました: {e}")
    # ★★★ エラー発生時もDiscordに通知する ★★★
    error_payload = {'content': f'スクリプトの実行中にエラーが発生しました。\n```\n{e}\n```'}
    requests.post(webhook_url, data=error_payload)

finally:
    driver.quit()
    print("処理が完了しました。")
