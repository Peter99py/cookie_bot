import cv2
import numpy as np
from mss import mss
from src.window_finder.window_finder import Beholder
import time


# cv2.circle(store_debug_img, centro, raio, cor, espessura)

class CookieVision:
    def __init__(self, debug=False):
        self.sct = mss()
        self.debug = debug
        
        # H é cor
        # S é saturação, mais alto é cor viva e sólida, mais baixo é cor transparente/branca
        # V é brilho, quanto mais baixo, mais preto
        self.config_golden = {
            "name": "golden",
            "lower": np.array([20, 146, 80]),
            "upper": np.array([25, 255, 190])
        }
        self.config_wrath = {
            "name": "wrath",
            "lower": np.array([1, 200, 98]),
            "upper": np.array([10, 230, 100])
            }

        self.min_opacidade = 240

        self.count_golden = 0
        self.count_wrath = 0
        
        self.beholder = Beholder()
        self.hwnd = self.beholder.hwnd
        self.rect = self.beholder.rect

        self.template_pop_up = cv2.imread("src/assets/fechar_pop_up.png")
        self.template_hand_of_fate = cv2.imread("src/assets/hand_of_fate.png")
        self.check_store_templates = {
            "milk_button": cv2.imread("src/assets/milk_button.png"),
            "festive_biscuit": cv2.imread("src/assets/festive_biscuit_button.png"),
            "ghostly biscuit": cv2.imread("src/assets/ghostly_biscuits_button.png")
        }
        """
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
            "alchemy_lab_button": cv2.imread("src/assets/alchemy_lab_button.png"),
            "portal_button": cv2.imread("src/assets/portal_button.png"),
            "time_machine_button": cv2.imread("src/assets/time_machine_button.png"),
            "antim_condenser_button": cv2.imread("src/assets/antim_condenser_button.png"),
            "prism_button": cv2.imread("src/assets/prism_button.png"),
            "chancemaker_button": cv2.imread("src/assets/chancemaker_button.png"),
            "fractal_engine_button": cv2.imread("src/assets/fractal_engine_button.png")
        }
        self.templates_structures = dict(reversed(self.templates_structures.items()))

        self.structures_dimensions = {}
        for name, template in self.templates_structures.items():
            self.structures_dimensions[name] = template.shape[:2]
        """

        # Largura dos blocos
        # Bloco da esquerda
        self.left_block_x_start = int(self.rect["left"])
        self.left_block_w = int(self.rect["width"] * 0.3020833333)
        # Bloco da direita (Loja)
        self.right_block_x_start = int(self.rect["width"] - self.rect["width"] * 0.1666666666)
        self.right_block_w = int(self.rect["width"] * 0.16)
        # Bloco do meio
        self.middle_block_x_start = self.left_block_x_start + self.left_block_w
        self.middle_block_w = self.rect["width"] - self.left_block_w - self.right_block_w
        # Bloco Upgrades
        self.upgrade_y_start = int(self.rect["height"] * 0.0787037037)
        self.upgrade_h = int(self.rect["height"] * 0.0509259259)
        self.upgrade_w = int(self.right_block_w * 0.4)
        # Bloco Structures
        self.structures_y_start = int(self.upgrade_y_start + self.rect["height"] * 0.1)
        self.structures_w = int(self.right_block_w * 0.94)
        self.structures_h = int(self.rect["height"] - self.structures_y_start - self.rect["height"] * 0.0462962962)

        self.pls_god= []
        self.pls_god_can_buy = []
    

    def check_store_y(self):

        store_x_start = self.right_block_x_start
        righ_block_w = self.right_block_w

        upgrade_y_start = self.upgrade_y_start

        raw_upgrades = np.array(self.sct.grab({
            "top": 2 + upgrade_y_start,
            "left": self.rect["left"] + store_x_start,
            "width": righ_block_w,
            "height": self.rect["height"]
        }))

        img_bgr = cv2.cvtColor(raw_upgrades, cv2.COLOR_BGRA2BGR)
        threshold = 0.9

        for name, template in self.check_store_templates.items():
            res = cv2.matchTemplate(img_bgr, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            print(f"1 º Check - template {name} - Valor: {max_val}")

            if max_val >= threshold:
                self.upgrade_y_start += 76
                self.structures_y_start += 76
                self.structures_h -= 76
                print("Sucesso no 1º Check")

                return            

        print("\nReconhecimento do ícone falhou, checando novamente a altura da loja")
        
        raw_upgrades2 = np.array(self.sct.grab({
            "top": 2 + upgrade_y_start,
            "left": self.rect["left"] + store_x_start,
            "width": righ_block_w,
            "height": self.rect["height"]
            }))
        
        img_bgr2 = cv2.cvtColor(raw_upgrades2, cv2.COLOR_BGRA2BGR)

        for name2, template2 in self.check_store_templates.items():
            res2 = cv2.matchTemplate(img_bgr2, template2, cv2.TM_CCOEFF_NORMED)
            _, max_val2, _, max_loc2 = cv2.minMaxLoc(res2)

            print(f"2 º Check - template {name2} - Valor: {max_val2}")

            if max_val2 >= threshold:
                self.upgrade_y_start += 76
                self.structures_y_start += 76
                self.structures_h -= 76
                print("Sucesso no 2º check.")
                return  

        print("Matendo a altura da loja como default.")


    def rect_check(self):
        # Atualiza o rect para a posição atual do beholder
        new_rect = self.beholder.get_window_rect()
        return new_rect == self.rect

    
    def get_screenshot(self):
        if self.rect:
            screenshot = np.array(self.sct.grab(self.rect))
            return screenshot


    def get_upgrade(self):

        store_x_start = self.right_block_x_start
        upgrade_w = self.upgrade_w

        upgrade_y_start = self.upgrade_y_start
        upgrade_height = self.upgrade_h

        raw_upgrades = np.array(self.sct.grab({
            "top": 2 + upgrade_y_start,
            "left": self.rect["left"] + store_x_start,
            "width": upgrade_w,
            "height": upgrade_height
        }))

        img_bgr = cv2.cvtColor(raw_upgrades, cv2.COLOR_BGRA2BGR)
        img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l_channel = img_lab[:, :, 0]
        
        rectangle_y, rectangle_h, rectangle_x, rectangle_w = 1, 55, 1, 55
        roi_upgrade = l_channel[rectangle_y:rectangle_h, rectangle_x:rectangle_w]

        pixels = roi_upgrade.flatten()

        pixels_ordenados = np.sort(pixels)
        
        quantidade_top = int(len(pixels_ordenados) * 0.15)
        top_pixels = pixels_ordenados[-quantidade_top:]
        
        brilho_upgrade = np.mean(top_pixels)

        pode_comprar = brilho_upgrade >= 120

        self.pls_god.append(brilho_upgrade)
        if self.debug:
            
            print(f"Brilho do upgrade: {brilho_upgrade}")
            debug_img = l_channel.copy()
            cv2.rectangle(debug_img, (rectangle_x, rectangle_y), (rectangle_w, rectangle_h), (255, 255, 255), 2)
            cv2.putText(debug_img, "ROI", (rectangle_x + 1, rectangle_y + 1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow("Debug Upgrades", debug_img)
            cv2.waitKey(1)

        if pode_comprar:
            self.pls_god_can_buy.append(brilho_upgrade)
            cX_real = store_x_start + (rectangle_w // 2)
            cY_real = upgrade_y_start + (rectangle_h // 2)
            return (cX_real, cY_real)
            
        return None


    def get_structure(self):
            store_x_start = self.right_block_x_start
            
            structures_y_start = self.structures_y_start
            structures_w = self.structures_w
            structures_h = self.structures_h

            raw_store = np.array(self.sct.grab({
                "top": structures_y_start,
                "left": self.rect["left"] + store_x_start,
                "width": structures_w,
                "height": structures_h
            }))

            img_bgr = cv2.cvtColor(raw_store, cv2.COLOR_BGRA2BGR)
            hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            s_channel = hsv[:, :, 1]
            v_channel = hsv[:, :, 2]
            
            v_channel = cv2.subtract(v_channel, (s_channel * 0.1).astype(np.uint8))
            v_channel = cv2.convertScaleAbs(v_channel, alpha=1, beta=60)

            if self.debug:
                store_debug_img = v_channel.copy()

            target = [None]
            
            box_size = 40
            step = 20
            threshold = 210

            found_in_row = False
            
            for y in range(structures_h - box_size, 0, -step):
                
                best_block_in_row = None
                max_brightness_row = 0

                for x in range(0, structures_w - box_size, step):
                    
                    roi = v_channel[y : y + box_size, x : x + box_size]
                    
                    avg_brightness = np.mean(roi)

                    if self.debug:
                        cv2.rectangle(store_debug_img, (x, y), (x + box_size, y + box_size), (50, 50, 50), 1)

                    if avg_brightness > threshold:

                        if avg_brightness > max_brightness_row:
                            max_brightness_row = avg_brightness
                            center_x = x + (box_size // 2)
                            center_y = y + (box_size // 2)
                            
                            best_block_in_row = (center_x, center_y, avg_brightness, x, y)
                
                if best_block_in_row:
                    cx, cy, brilho, rx, ry = best_block_in_row
                    
                    cx_real = store_x_start + cx
                    cy_real = structures_y_start + cy
                    

                    target = [(cx_real, cy_real)]
                    
                    if self.debug:
                        cv2.rectangle(store_debug_img, (rx, ry), (rx + box_size, ry + box_size), (0, 255, 0), 2)
                        print(f"Estrutura encontrada (X={cx_real}) - (Y={cy_real}) - Brilho: {brilho:.2f}")
                    
                    found_in_row = True
                    break

            if self.debug:
                cv2.imshow("Debug Loja - Get structure", store_debug_img)
                cv2.waitKey(1)

            return target
    

    def find_any_golden(self):

        screenshot = self.get_screenshot()

        alpha_channel = screenshot[:, :, 3]
        _, alpha_mask = cv2.threshold(alpha_channel, self.min_opacidade, 255, cv2.THRESH_BINARY)

        img_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        if self.count_wrath > self.count_golden:
            search_order = [self.config_wrath, self.config_golden]
            #print(f"Prioridade: Vermelhos ({self.count_wrath} vs {self.count_golden})")
        else:
            search_order = [self.config_golden, self.config_wrath]
            #print(f"Prioridade: Dourados ({self.count_golden} vs {self.count_wrath})")

        for color_cfg in search_order:
            color_mask = cv2.inRange(hsv, color_cfg["lower"], color_cfg["upper"])
            combined_mask = cv2.bitwise_and(color_mask, alpha_mask)

            kernel = np.ones((10, 10), np.uint8) 
            mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.dilate(mask, kernel, iterations=1)
  
            if self.debug:
                escala = 0.4
                debug_img = cv2.resize(mask, (0,0), fx=escala, fy=escala)
                cv2.imshow(f"Debug - {color_cfg['name']}", debug_img)
                cv2.waitKey(1)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w >= 60 and h >= 60:
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                    
                        if self.count_golden == 10 or self.count_wrath == 10:
                            self.count_golden = 0
                            self.count_wrath = 0

                        if color_cfg["name"] == "golden":
                            self.count_golden += 1
                        else:
                            self.count_wrath += 1

                        return (cX, cY, color_cfg["name"])

        return None
    

    def pop_up_killer(self):

        pop_ups_x_start = self.middle_block_x_start
        pop_ups_w = self.middle_block_w

        pop_ups_y_start = int(self.rect["top"] + 50)
        pop_ups_height = int(self.rect["height"] - 50)

        raw_pop_ups = np.array(self.sct.grab({
            "top": pop_ups_y_start,
            "left": pop_ups_x_start,
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

                real_center_y = pop_ups_y_start + center_y - 12
                real_center_x = self.left_block_w + center_x
                points.append((real_center_x, real_center_y))

                if self.debug:
                    cv2.circle(debug_img, (center_x, center_y), 10, (0, 255, 0), 2)

        if self.debug:
            cv2.imshow("Debug - Pop-up-killer", debug_img) 
            cv2.waitKey(1)

        return points[-1] if points else None


    def hand_of_fate(self):
        
        middle_x_start = self.middle_block_x_start
        middle_w = self.middle_block_w

        raw_middle = np.array(self.sct.grab({
            "top": self.rect["top"] + 31,
            "left": middle_x_start,
            "width": middle_w,
            "height": self.rect["height"]}))
        
        template_y, template_x = self.template_hand_of_fate.shape[:2]
        img_bgr = cv2.cvtColor(raw_middle, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(img_bgr, self.template_hand_of_fate, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        threshold = 0.9

        if max_val >= threshold:
            top = max_loc[1]
            left = max_loc[0]

            center_y = top + template_y // 2
            center_x = left + template_x // 2

            real_center_y = center_y
            real_center_x = self.left_block_w + center_x

            if self.debug:
                debug_img = img_bgr.copy()

            if self.debug:
                cv2.circle(debug_img, (center_x, center_y), 10, (0, 255, 0), 2)
                cv2.imshow("Debug - hand-of-fate", debug_img)
                cv2.waitKey(1)

            return real_center_x, real_center_y, max_val


    def vision_test(self, vision_x, vision_y, vision_w, vision_h, x, y):

        raw_store = np.array(self.sct.grab({
            "top": vision_y,
            "left": self.rect["left"] + vision_x,
            "width": vision_w,
            "height": vision_h
        }))

        img_bgr = cv2.cvtColor(raw_store, cv2.COLOR_BGRA2BGR)

        if self.debug:
            cv2.circle(img_bgr, (x, y), 5, (0, 255, 0), -1)

            cv2.imshow("Teste por visao", img_bgr)
            cv2.waitKey(15)
        
        return True