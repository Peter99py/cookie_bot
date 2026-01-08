import cv2
import numpy as np
from mss import mss
from src.window_finder.window_finder import Beholder

class CookieVision:
    def __init__(self, debug=False):
        self.sct = mss()
        self.debug = debug
        
        # H é cor
        # S é saturação, mais alto é cor viva e sólida, mais baixo é cor transparente/branca
        # V é brilho, quanto mais baixo, mais preto
        self.lower_golden = np.array([20, 140, 85]) 
        self.upper_golden = np.array([33, 255, 190])
        self.min_opacidade = 235
        
        self.beholder = Beholder()
        self.hwnd = self.beholder.hwnd
        self.rect = self.beholder.rect

        self.template_pop_up = cv2.imread("src/assets/fechar_pop_up.png")
        self.template_hand_of_fate = cv2.imread("src/assets/hand_of_fate.png")

        # Templates estruturas
        self.template_cursor_button = cv2.imread("src/assets/cursor_button.png")
        self.template_grandma_button = cv2.imread("src/assets/grandma_button.png")
        self.template_farm_button = cv2.imread("src/assets/farm_button.png")

        # Largura dos blocos
        # Bloco do meio
        self.middle_block_x_start = int(self.rect["width"] * 0.3083333333)
        self.middle_block_w = int(self.rect["width"] * 0.5208333333)
        # Bloco da direita (Loja)
        self.store_x_start = int(self.middle_block_x_start + self.middle_block_w)
        self.store_w = int(self.rect["width"] * 0.1666666666)
            # Bloco Upgrades
        self.upgrade_y_start = int(self.rect["height"] * 0.0787037037)
        self.upgrade_h = int(self.rect["height"] * 0.0509259259)

    
    def get_screenshot(self):
        if self.rect:
            screenshot = np.array(self.sct.grab(self.rect))
            return screenshot


    def get_upgrade(self):

        store_x_start = self.store_x_start
        store_w = self.store_w

        upgrade_y_start = self.upgrade_y_start
        upgrade_height = self.upgrade_h

        raw_upgrades = np.array(self.sct.grab({
            "top": 2 + upgrade_y_start,
            "left": self.rect["left"] + store_x_start,
            "width": store_w,
            "height": upgrade_height
        }))

        img_bgr = cv2.cvtColor(raw_upgrades, cv2.COLOR_BGRA2BGR)
        v_channel = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)[:, :, 2]
        v_channel = cv2.convertScaleAbs(v_channel, alpha=3)

        upgrade_size = 50
        roi_upgrade = v_channel[10:55, 5:upgrade_size]
        brilho_upgrade = np.mean(roi_upgrade)

        pode_comprar = brilho_upgrade > 170

        if self.debug:

            debug_img = v_channel.copy()
            cv2.rectangle(debug_img, (10, 5), (55, upgrade_size), 255, 2)

            local_x = (upgrade_size // 2)
            local_y = (upgrade_size // 2)
            
            if pode_comprar:
                
                cv2.circle(debug_img, (local_x, local_y), 10, 255, -1) 
                cv2.circle(debug_img, (local_x, local_y), 12, 0, 2)
                
                print(f"DEBUG: Upgrade disponível! Brilho: {brilho_upgrade}")

            cv2.imshow("Debug Upgrades", debug_img)
            cv2.waitKey(1)

        if pode_comprar:

            cX_real = store_x_start + (upgrade_size // 2)
            cY_real = upgrade_y_start + (upgrade_size // 2)
            return (cX_real, cY_real)
            
        return None


    def get_structure(self):
        # largura da loja
        store_x_start = self.store_x_start
        store_w = self.store_w

        raw_store = np.array(self.sct.grab({
            "top": int(0),
            "left": self.rect["left"] + store_x_start,
            "width": store_w,
            "height": self.rect["height"]
        }))

        img_bgr = cv2.cvtColor(raw_store, cv2.COLOR_BGRA2BGR)
        v_channel = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)[:, :, 2]
        v_channel = cv2.convertScaleAbs(v_channel, alpha=1.5)

        buyable_coords = []
        item_h = 64
        
        if self.debug:
            store_debug_img = v_channel.copy()

        for i in range(14):
            y_start = i * item_h
            y_end = y_start + item_h
            if y_end > raw_store.shape[0]: break
                
            roi_v = v_channel[y_start:y_end, :]
            brilho_medio = np.mean(roi_v)

            pode_comprar = brilho_medio > 180
            
            if self.debug:
                cor_rect = (0, 255, 0) if pode_comprar else (0, 0, 255)
                cv2.rectangle(store_debug_img, (0, y_start), (store_w, y_end), cor_rect, 2)

            if pode_comprar:
                local_cX = store_w // 2
                local_cY = y_start + (item_h // 2)

                if self.debug:
                    cv2.circle(store_debug_img, (local_cX, local_cY), 10, (255, 255, 255), -1) # Círculo branco
                    cv2.circle(store_debug_img, (local_cX, local_cY), 12, (0, 0, 0), 2)

                # Lista de onde clicar
                cX_real = store_x_start + local_cX
                cY_real = local_cY
                buyable_coords.append((cX_real, cY_real))

        if self.debug:
            cv2.imshow("Debug Loja - Brilho (V)", store_debug_img)
            cv2.waitKey(1)
            
            
        return buyable_coords


    def find_any_golden(self):

        screenshot = self.get_screenshot()

        alpha_channel = screenshot[:, :, 3]
        _, alpha_mask = cv2.threshold(alpha_channel, self.min_opacidade, 255, cv2.THRESH_BINARY)

        img_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        color_mask = cv2.inRange(hsv, self.lower_golden, self.upper_golden)

        combined_mask = cv2.bitwise_and(color_mask, alpha_mask)

        # Só Deus sabe o que é isso aqui embaixo
        kernel = np.ones((10, 10), np.uint8) 
        mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)
        
        if self.debug:
            escala = 0.4
            debug_img = cv2.resize(mask, (0,0), fx=escala, fy=escala)
            cv2.imshow("Debug - Filtro Anti-Efeito", debug_img)
            cv2.waitKey(1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w >= 50 and h >= 50:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    return (cX, cY)
        return None


    def close_pop_ups(self):

        pop_ups_x_start = int(self.rect["width"] * 0.5)
        pop_ups_w = int(self.rect["width"] * 0.2)

        pop_ups_y_start = int(self.rect["height"] * 0.6)
        pop_ups_height = int(self.rect["height"] * 0.5)

        raw_pop_ups = np.array(self.sct.grab({
            "top": self.rect["top"] + pop_ups_y_start,
            "left": self.rect["left"] + pop_ups_x_start,
            "width": pop_ups_w,
            "height": pop_ups_height
        }))

        template_y, template_x = self.template_pop_up.shape[:2]
        img_bgr = cv2.cvtColor(raw_pop_ups, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(img_bgr, self.template_pop_up, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8

        locations = np.where(result >= threshold)
        locations = np.column_stack((locations[1], locations[0]))
        locations_group = np.unique((locations // 10), axis=0) * 10


        if self.debug:
            debug_img = img_bgr.copy()

        points = []

        if locations_group.size > 0:
            for x, y in locations_group:
                center_y = y + template_y // 2
                center_x = x + template_x // 2

                real_center_y = pop_ups_y_start + center_y - 23 # 23 é compensação da barra da janela do windows
                real_center_x = pop_ups_x_start + center_x
                points.append((real_center_x, real_center_y))

                if self.debug:
                    cv2.circle(debug_img, (center_x, center_y), 15, (0, 255, 0), 2)

        if self.debug:
            cv2.imshow("Debug - Pop-up-killer", debug_img)
            cv2.waitKey(1)

        return points[0] if points else None
    
    def hand_of_fate(self):
        
        middle_x_start = self.middle_block_x_start
        middle_w = self.middle_block_w

        raw_middle = np.array(self.sct.grab({
            "top": self.rect["top"],
            "left": self.rect["left"] + middle_x_start,
            "width": middle_w,
            "height": self.rect["height"]}))
        
        template_y, template_x = self.template_hand_of_fate.shape[:2]
        img_bgr = cv2.cvtColor(raw_middle, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(img_bgr, self.template_hand_of_fate, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        threshold = 0.91

        if max_val < threshold:
            return None
        
        top = max_loc[1]
        left = max_loc[0]

        center_y = top + template_y // 2
        center_x = left + template_x // 2

        real_center_y = center_y
        real_center_x = middle_x_start + center_x

        if self.debug:
            debug_img = img_bgr.copy()

        if self.debug:
            cv2.circle(debug_img, (center_x, center_y), 10, (0, 255, 0), 2)
            cv2.imshow("Debug - hand-of-fate", debug_img)
            cv2.waitKey(1)

        return real_center_x, real_center_y, max_val