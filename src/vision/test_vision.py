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
        self.templates_structures = {
            "cursor_button": cv2.imread("src/assets/cursor_button.png"),
            "grandma_button": cv2.imread("src/assets/grandma_button.png"),
            "farm_button": cv2.imread("src/assets/farm_button.png"),
            "mine_button": cv2.imread("src/assets/mine_button.png"),
            "factory_button": cv2.imread("src/assets/factory_button.png"),
            "bank_button": cv2.imread("src/assets/bank_button.png"),
            "temple_button": cv2.imread("src/assets/temple_button.png"),
            "wizard_tower_button": cv2.imread("src/assets/wizard_tower_button.png"),
            "shipment_button": cv2.imread("src/assets/shipment_button.png"),
            "alchemy_lab_button": cv2.imread("src/assets/alchemy_lab_button.png")
        }
        self.templates_structures = dict(reversed(self.templates_structures.items()))

        self.structures_dimensions = {}
        for name, template in self.templates_structures.items():
            self.structures_dimensions[name] = template.shape[:2]

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
        print(brilho_upgrade)

        pode_comprar = brilho_upgrade > 170

        target = None

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

            cx_real = store_x_start + (upgrade_size // 2)
            cy_real = upgrade_y_start + (upgrade_size // 2)
            
        return (cx_real, cy_real)
    

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
        v_channel = cv2.convertScaleAbs(v_channel, alpha=3)

        if self.debug:
            store_debug_img = v_channel.copy()

        target = None

        for name, template in self.templates_structures.items():
            res = cv2.matchTemplate(img_bgr, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val >= 0.8:
                w, h = self.structures_dimensions[name]
                
                roi_v = v_channel[max_loc[1]:max_loc[1]+h, max_loc[0]:max_loc[0]+w]
                brightness_mean = np.mean(roi_v)
                can_buy = brightness_mean > 240
                
                center_x = max_loc[0]
                center_y = max_loc[1]

                if can_buy:
                    cx_real = store_x_start + center_x
                    cy_real = center_y

                    if self.debug:
                        cv2.circle(store_debug_img, (cx_real, cy_real), 15, (0, 255, 0), 2)
                        print(f"DEBUG: Estrutura '{name}' disponível para compra! Brilho: {brightness_mean}")

                    target = (cx_real, cy_real)
                    break

        if self.debug:
            cv2.imshow("Debug Loja - Estruturas", store_debug_img)
            cv2.waitKey(1)

        return target


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