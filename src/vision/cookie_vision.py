import cv2
import numpy as np
from mss import mss
import win32gui

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

        self.hwnd = self.encontrar_janela_cookie()
        self.rect = self.get_window_rect()

    def encontrar_janela_cookie(self):
    # Busca o identificador (HWND) da janela.
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd):
                titulo = win32gui.GetWindowText(hwnd)
                if titulo.endswith("Cookie Clicker"):
                    hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds[0] if hwnds else None

    def get_window_rect(self):

        if self.hwnd:
            rect = win32gui.GetWindowRect(self.hwnd)
            return {"top": rect[1], "left": rect[0], "width": rect[2]-rect[0], "height": rect[3]-rect[1]}
        return None
    
    def get_screenshot(self):
        if self.rect:
            screenshot = np.array(self.sct.grab(self.rect))
            return screenshot       

    def get_store_status(self):
        # largura da loja
        store_w = int(self.rect["width"] * 0.17)
        store_x_start = self.rect["width"] - store_w
        
        # altura da loja
        offset_y = int(self.rect["height"] * 0.188)
        height_loja = self.rect["height"] - offset_y

        raw_store = np.array(self.sct.grab({
            "top": self.rect["top"] + offset_y,
            "left": self.rect["left"] + store_x_start,
            "width": store_w,
            "height": height_loja
        }))

        img_bgr = cv2.cvtColor(raw_store, cv2.COLOR_BGRA2BGR)
        v_channel = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)[:, :, 2]
        v_channel = cv2.convertScaleAbs(v_channel, alpha=1.5, beta=0)

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
                cY_real = offset_y + local_cY - 30
                buyable_coords.append((cX_real, cY_real))

        if self.debug:
            cv2.imshow("Debug Loja - Brilho (V)", store_debug_img)
            
        return buyable_coords
    

    def get_upgrade_status(self):

        store_w = int(self.rect["width"] * 0.17)
        store_x_start = self.rect["width"] - store_w

        upgrade_y_start = int(self.rect["height"] * 0.085) 
        upgrade_height = int(self.rect["height"] * 0.06)

        raw_upgrades = np.array(self.sct.grab({
            "top": self.rect["top"] + upgrade_y_start,
            "left": self.rect["left"] + store_x_start,
            "width": store_w,
            "height": upgrade_height
        }))

        img_bgr = cv2.cvtColor(raw_upgrades, cv2.COLOR_BGRA2BGR)
        v_channel = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)[:, :, 2]
        v_channel = cv2.convertScaleAbs(v_channel, alpha=2.0, beta=50)

        upgrade_size = 60
        roi_upgrade = v_channel[5:upgrade_size, 5:upgrade_size]
        brilho_upgrade = np.mean(roi_upgrade)

        pode_comprar = brilho_upgrade > 170

        if self.debug:

            debug_img = v_channel.copy()

            local_x = (upgrade_size // 2)
            local_y = (upgrade_size // 2)
            
            if pode_comprar:
                
                cv2.circle(debug_img, (local_x, local_y), 10, 255, -1) 
                cv2.circle(debug_img, (local_x, local_y), 12, 0, 2)
                
                print(f"DEBUG: Upgrade disponível! Brilho: {brilho_upgrade}")

            cv2.imshow("Debug Upgrades", debug_img)

        if pode_comprar:

            cX_real = store_x_start + (upgrade_size // 2) + 5
            cY_real = upgrade_y_start + (upgrade_size // 2) - 30 + 5 # 30 é compensação da barra da janela do windows
            return (cX_real, cY_real)
            
        return None


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

        pop_ups_w = int(self.rect["width"] * 0.17)
        pop_ups_x_start = self.rect["width"] - pop_ups_w

        pop_ups_y_start = int(self.rect["height"] * 0.085) 
        pop_ups_height = int(self.rect["height"] * 0.06)

        raw_pop_ups = np.array(self.sct.grab({
            "top": self.rect["top"] + pop_ups_y_start,
            "left": self.rect["left"] + pop_ups_x_start,
            "width": pop_ups_w,
            "height": pop_ups_height
        }))

        template = cv2.imread("src/vision/assets/close_popup.png")
        template_y, template_x = template.shape[:2]
        img_bgr = cv2.cvtColor(raw_pop_ups, cv2.COLOR_BGRA2BGR)

        result = cv2.matchTemplate(img_bgr, template, cv2.TM_CCOEFF_NORMED)

        threshold = 0.8

        locations = np.where(result >= threshold)

        if self.debug:
            debug_img = img_bgr.copy()
        
        if locations:
            pass
        else:
            return None

        points = []

        for pt in locations:
            center_y = pt[0] + template_y // 2
            center_x = pt[1] + template_x // 2

            real_center_y = pop_ups_y_start + center_y - 30 # 30 é compensação da barra da janela do windows
            real_center_x = pop_ups_x_start + center_x
            points.append((real_center_x, real_center_y))

            if self.debug:
                cv2.circle(debug_img, (center_x, center_y), 20, (0, 255, 0), 2)

        if self.debug:
            cv2.imshow("Debug - Pop-up-killer", debug_img)
        
        return points[0]