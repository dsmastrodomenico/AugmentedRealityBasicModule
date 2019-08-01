import json
import sys
import cv2 as cv 
import numpy as np 
from algorithms.controller import control_camera 


class BodyTrackerSystem(): 

    cap, scaling_factor, num_frames_to_track, num_frames_jump, tracking_params = control_camera().camera()

    def compute_feature_points(self, tracking_paths, prev_img, current_img):
        feature_points = [tp[-1] for tp in tracking_paths]
        
        # Vector de puntos 2D para los cuales es necesario encontrar el flujo.
        feature_points_0 = np.float32(feature_points).reshape(-1, 1, 2) 

        feature_points_1, status_1, err_1 = cv.calcOpticalFlowPyrLK(prev_img, 
            current_img, feature_points_0, None, **self.tracking_params) 
        feature_points_0_rev, status_2, err_2 = cv.calcOpticalFlowPyrLK(current_img,
            prev_img, feature_points_1, None, **self.tracking_params)

        # Calcular la diferencia de los puntos de caracteristicas 
        diff_feature_points = abs(feature_points_0-feature_points_0_rev).reshape(-1, 2).max(-1) 

        # Umbral y mantener solo los puntos buenos. 
        good_points = diff_feature_points < 1
        return feature_points_1.reshape(-1, 2), good_points

        # Extraer area de interes basada en las rutas de seguimiento (tracking_paths)


    # En caso de que no haya ninguno, se utiliza todo el cuadro.
    def calculate_region_of_interest(self, frame, tracking_paths):
        mask = np.zeros_like(frame) 
        mask[:] = 255 
        for x, y in [np.int32(tp[-1]) for tp in tracking_paths]: 
            cv.circle(mask, (x, y), 6, 0, -1) 
        return mask

    def add_tracking_paths(self, frame, tracking_paths):
        mask = self.calculate_region_of_interest(frame, tracking_paths)

        # Extrae buenas caracteristicas para seguir. 
        feature_points = cv.goodFeaturesToTrack(frame, mask = mask, maxCorners = 500, 
            qualityLevel = 0.3, minDistance = 7, blockSize = 7) 

        if feature_points is not None: 
            for x, y in np.float32(feature_points).reshape(-1, 2): 
                tracking_paths.append([(x, y)])


    def start_tracking(self): 
        tracking_paths = [] 
        frame_index = 0 

        # Iterar hasta que el usuario presione la tecla ESC. 
        while True: 
            # leer el marco de entrada 
            ret, frame = self.cap.read() 

            # bajar la muestra del marco de entrada 
            frame = cv.resize(frame, None, fx=self.scaling_factor, fy=self.scaling_factor,
                interpolation=cv.INTER_AREA) 

            frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY) 
            output_img = frame.copy() 
            

            if len(tracking_paths) > 0: 
                prev_img, current_img = prev_gray, frame_gray
                # Calcular puntos de caracteristicas utilizando flujo optico. 
                
                feature_points, good_points = self.compute_feature_points(tracking_paths,
                    prev_img, current_img)

                new_tracking_paths = []
                for tp, (x, y), good_points_flag in zip(tracking_paths, feature_points, good_points): 
                    if not good_points_flag: continue 

                    tp.append((x, y)) 

                    # Usando la estructura de cola, primero en entrar, primero en salir
                    if len(tp) > self.num_frames_to_track: del tp[0] 

                    new_tracking_paths.append(tp) 

                    # dibujar circulos verdes en la parte superior de la imagen de salida 
                    cv.circle(output_img, (x, y), 3, (0, 255, 0), -1) 

                tracking_paths = new_tracking_paths 

                # dibujar lineas en la parte superior de la imagen de salida 
                point_paths = [np.int32(tp) for tp in tracking_paths]
                cv.polylines(output_img, point_paths, False, (0, 150, 0)) 

            # 'if' condicion para saltar cada 'n' cuadros 
            if not frame_index % self.num_frames_jump: 
                self.add_tracking_paths(frame_gray, tracking_paths)

            frame_index += 1 
            prev_gray = frame_gray 

            cv.imshow('Flujo Optico', output_img) 

            # Compruebe si el usuario ha pulsado la tecla ESC.
            c = cv.waitKey(1) 
            if c == 27: 
                break
        self.cap.release() 
        cv.destroyAllWindows()