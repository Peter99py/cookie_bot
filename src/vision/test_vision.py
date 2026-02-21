import cv2
import numpy as np
from src.vision.cookie_vision import CookieVision


class CookieVisionTest(CookieVision):
    """Variante de CookieVision com thresholds/parâmetros ajustados para testes.

    Herda toda a lógica de CookieVision e sobrescreve apenas o que difere:
      - config_wrath (saturação upper 230 vs 220)
      - upgrade_h, upgrade_w (dimensões diferentes)
      - structures_y_start (campo dedicado)
      - get_upgrade() (usa LAB brightness em vez de HSV scan)
      - get_structure() (threshold 210 vs 215, center_y calculado diferente)
      - check_store_y() (também ajusta structures_y_start)
      - Templates de estrutura (ativos, enquanto no cookie_vision estão comentados)
    """

    def __init__(self, debug=False):
        super().__init__(debug=debug)

        # Sobrescreve config_wrath com saturação upper diferente
        self.config_wrath = {
            "name": "wrath",
            "lower": np.array([1, 200, 98]),
            "upper": np.array([10, 230, 100])
        }

        # Dimensões de upgrade diferentes
        self.upgrade_h = int(self.rect["height"] * 0.0509259259)
        self.upgrade_w = int(self.right_block_w * 0.4)

        # Campo dedicado para structures_y_start
        self.structures_y_start = int(self.upgrade_y_start + self.rect["height"] * 0.1)
        self.structures_h = int(
            self.rect["height"] - self.structures_y_start
            - self.rect["height"] * 0.0462962962
        )

        # Templates de estrutura (ativos nesta variante)
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

        self.pls_god = []
        self.pls_god_can_buy = []

    # ----- Métodos sobrescritos com lógica diferente -----

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
            cv2.rectangle(debug_img, (rectangle_x, rectangle_y),
                          (rectangle_w, rectangle_h), (255, 255, 255), 2)
            cv2.putText(debug_img, "ROI", (rectangle_x + 1, rectangle_y + 1),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
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

        for y in range(structures_h - box_size, 0, -step):

            best_block_in_row = None
            max_brightness_row = 0

            for x in range(0, structures_w - box_size, step):

                roi = v_channel[y : y + box_size, x : x + box_size]
                avg_brightness = np.mean(roi)

                if self.debug:
                    cv2.rectangle(store_debug_img, (x, y),
                                  (x + box_size, y + box_size), (50, 50, 50), 1)

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
                    cv2.rectangle(store_debug_img, (rx, ry),
                                  (rx + box_size, ry + box_size), (0, 255, 0), 2)
                    print(f"Estrutura encontrada (X={cx_real}) - (Y={cy_real}) - Brilho: {brilho:.2f}")

                break

        if self.debug:
            cv2.imshow("Debug Loja - Get structure", store_debug_img)
            cv2.waitKey(1)

        return target