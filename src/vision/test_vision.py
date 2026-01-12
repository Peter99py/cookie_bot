import cv2
import numpy as np
from mss import mss
from src.window_finder.window_finder import Beholder


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
            "upper": np.array([10, 255, 100])
            }

        self.min_opacidade = 230

        self.count_golden = 0
        self.count_wrath = 0
        
        self.beholder = Beholder()
        self.hwnd = self.beholder.hwnd
        self.rect = self.beholder.rect

        self.template_pop_up = cv2.imread("src/assets/fechar_pop_up.png")
        self.template_hand_of_fate = cv2.imread("src/assets/hand_of_fate.png")
        self.template_gardenPlants = cv2.imread("src/assets/gardenPlants.png")
        self.template_milk_colors = cv2.imread("src/assets/icons.png")

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

        self.template_milk = cv2.imread("src/assets/milk_button.png")

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
    

    def check_store_y(self):

        store_x_start = self.store_x_start
        store_w = self.store_w

        upgrade_y_start = self.upgrade_y_start

        raw_upgrades = np.array(self.sct.grab({
            "top": 2 + upgrade_y_start,
            "left": self.rect["left"] + store_x_start,
            "width": store_w,
            "height": self.rect["height"]
        }))

        img_bgr = cv2.cvtColor(raw_upgrades, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(img_bgr, self.template_milk, cv2.TM_CCOEFF_NORMED)

        _, max_val, _, _ = cv2.minMaxLoc(result)

        threshold = 0.85

        if max_val >= threshold:
            self.upgrade_y_start += 76


    def rect_check(self):
        # Atualiza o rect para a posição atual do beholder
        new_rect = self.beholder.get_window_rect()
        return new_rect == self.rect

    
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
        v_channel = cv2.convertScaleAbs(v_channel, alpha=2, beta=92)

        upgrade_size = 50
        roi_upgrade = v_channel[10:55, 5:upgrade_size]
        brilho_upgrade = np.mean(roi_upgrade)

        pode_comprar = brilho_upgrade > 201

        if self.debug:

            print(f"Brilho do upgrade: {brilho_upgrade}")
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
        v_channel = cv2.convertScaleAbs(v_channel, alpha=2, beta=-100)

        if self.debug:
            store_debug_img = v_channel.copy()

        target = [None, None]

        for name, template in self.templates_structures.items():
            res = cv2.matchTemplate(img_bgr, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val >= 0.8:
                w, h = self.structures_dimensions[name]
                
                roi_v = v_channel[max_loc[1]:max_loc[1]+h, max_loc[0]:max_loc[0]+w]
                brightness_mean = np.mean(roi_v)
                can_buy = brightness_mean > 166

                center_x = max_loc[0] + 15
                center_y = max_loc[1] + 15

                if can_buy:
                    cx_real = store_x_start + center_x
                    cy_real = center_y

                    if self.debug:
                        cv2.circle(store_debug_img, (center_x, center_y), 15, (0, 255, 0), 2)
                        print(f"DEBUG: Estrutura '{name}' disponível para compra! Brilho: {brightness_mean}")

                    target = [(cx_real, cy_real), name]
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


    def grandma_plants(self, row, col):

        full_image = self.template_gardenPlants
        icon = full_image

        icon_size = 48

        y1 = row * icon_size
        y2 = y1 + icon_size
        x1 = col * icon_size
        x2 = x1 + icon_size

        icon = icon[y1:y2, x1:x2]

        if self.debug:
            #cv2.rectangle(full_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imshow("Recorte da planta", icon)
        return icon   


    def im_a_landlord(self):

        

        pass