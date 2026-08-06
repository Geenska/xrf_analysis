import os
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

# Diccionario de referencia con energías características de líneas XRF comunes (en keV)
XRF_ELEMENTS = {
    'Mg_Ka': (1.25, 'Kα', 'Magnesio (Mg)'),
    'Al_Ka': (1.49, 'Kα', 'Aluminio (Al)'),
    'Si_Ka': (1.74, 'Kα', 'Silicio (Si)'),
    'P_Ka': (2.01, 'Kα', 'Fósforo (P)'),
    'S_Ka': (2.31, 'Kα', 'Azufre (S)'),
    'Pb_Ma': (2.34, 'Mα', 'Plomo (Pb)'),
    'Cl_Ka': (2.62, 'Kα', 'Cloro (Cl)'),
    'Rh_La': (2.69, 'Lα', 'Rodio (Rh)'),
    'Pd_La': (2.84, 'Lα', 'Paladio (Pd)'),
    'Ar_Ka': (2.96, 'Kα', 'Argón (Ar)'),
    'Ag_La': (2.98, 'Lα', 'Plata (Ag)'),
    'Cd_La': (3.13, 'Lα', 'Cadmio (Cd)'),
    'K_Ka': (3.31, 'Kα', 'Potasio (K)'),
    'Sn_La': (3.44, 'Lα', 'Estaño (Sn)'),
    'Sb_La': (3.60, 'Lα', 'Antimonio (Sb)'),
    'Ca_Ka': (3.69, 'Kα', 'Calcio (Ca)'),
    'Ca_Kb': (4.01, 'Kβ', 'Calcio (Ca)'),
    'Ba_La': (4.47, 'Lα', 'Bario (Ba)'),
    'Ti_Ka': (4.51, 'Kα', 'Titanio (Ti)'),
    'Ti_Kb': (4.93, 'Kβ', 'Titanio (Ti)'),
    'Cr_Ka': (5.41, 'Kα', 'Cromo (Cr)'),
    'Cr_Kb': (5.95, 'Kβ', 'Cromo (Cr)'),
    'Mn_Ka': (5.90, 'Kα', 'Manganeso (Mn)'),
    'Fe_Ka': (6.40, 'Kα', 'Hierro (Fe)'),
    'Fe_Kb': (7.06, 'Kβ', 'Hierro (Fe)'),
    'Co_Ka': (6.93, 'Kα', 'Cobalto (Co)'),
    'Ni_Ka': (7.48, 'Kα', 'Níquel (Ni)'),
    'Cu_Ka': (8.04, 'Kα', 'Cobre (Cu)'),
    'Cu_Kb': (8.90, 'Kβ', 'Cobre (Cu)'),
    'Zn_Ka': (8.63, 'Kα', 'Zinc (Zn)'),
    'Zn_Kb': (9.57, 'Kβ', 'Zinc (Zn)'),
    'Au_La': (9.71, 'Lα', 'Oro (Au)'),
    'Hg_La': (9.99, 'Lα', 'Mercurio (Hg)'),
    'As_Ka': (10.54, 'Kα', 'Arsénico (As)'),
    'Pb_La': (10.55, 'Lα', 'Plomo (Pb)'),
    'Bi_La': (10.84, 'Lα', 'Bismuto (Bi)'),
    'Au_Lb': (11.44, 'Lβ', 'Oro (Au)'),
    'Br_Ka': (11.92, 'Kα', 'Bromo (Br)'),
    'Pb_Lb': (12.61, 'Lβ', 'Plomo (Pb)'),
    'Bi_Lb': (13.02, 'Lβ', 'Bismuto (Bi)'),
    'Sr_Ka': (14.16, 'Kα', 'Estroncio (Sr)'),
    'Zr_Ka': (15.77, 'Kα', 'Zirconio (Zr)'),
    'Rh_Ka': (20.21, 'Kα', 'Rodio (Rh)'),
    'Pd_Ka': (21.18, 'Kα', 'Paladio (Pd)'),
    'Ag_Ka': (22.16, 'Kα', 'Plata (Ag)'),
    'Cd_Ka': (23.11, 'Kα', 'Cadmio (Cd)'),
    'Sn_Ka': (25.27, 'Kα', 'Estaño (Sn)'),
    'Sb_Ka': (26.36, 'Kα', 'Antimonio (Sb)'),
    'Rh_Kb': (22.72, 'Kβ', 'Rodio (Rh)')
}

def obtener_calibracion(dir_path):
    """
    Busca un archivo de calibración (.xlsx) en el directorio especificado.
    Retorna los coeficientes (slope, intercept) si los encuentra y son válidos, o None.
    """
    if not os.path.isdir(dir_path):
        return None
    try:
        filenames = os.listdir(dir_path)
    except Exception as e:
        print(f"[Calibración Warning] No se pudo listar el directorio {dir_path}: {e}")
        return None
    for f in filenames:
        if 'calibracion' in f.lower() and f.endswith('.xlsx'):
            ruta = os.path.join(dir_path, f)
            try:
                df = pd.read_excel(ruta).dropna()
                # Buscar columnas de interés por nombre
                idx_kev = -1
                idx_chan = -1
                for i, col in enumerate(df.columns):
                    col_lower = str(col).lower()
                    if 'kev' in col_lower:
                        idx_kev = i
                    elif 'channel' in col_lower or 'canal' in col_lower:
                        idx_chan = i
                
                if idx_kev != -1 and idx_chan != -1:
                    X = df.iloc[:, idx_chan].values
                    y = df.iloc[:, idx_kev].values
                    if len(X) >= 2:
                        slope, intercept = np.polyfit(X, y, 1)
                        return slope, intercept
            except Exception as e:
                print(f"[Calibración Warning] Error al leer calibración {f}: {e}")
    return None

def leer_pdz(ruta_archivo, calibracion=None):
    """
    Lee un archivo XRF .pdz usando pdz-tool.
    Retorna un diccionario con:
      - 'metadata': datos del disparo (tiempo vivo, voltaje, corriente)
      - 'datos': pandas DataFrame con columnas 'Energia_keV' y 'Cuentas'
    """
    from pdz_tool import PDZTool
    pdz = PDZTool(ruta_archivo)
    data = pdz.parse()
    
    header = data.get('File Header', {})
    spectrum = data.get('XRF Spectrum', {})
    
    num_channels = spectrum.get('num_channels')
    if num_channels is None:
        num_channels = 2048
    ev_per_channel = spectrum.get('ev_per_channel')
    if ev_per_channel is None:
        ev_per_channel = 20.0
    counts = spectrum.get('spectrum_data', [])
    
    # Calcular energía en keV usando calibración si está disponible
    if calibracion:
        slope, intercept = calibracion
        energias = [i * slope + intercept for i in range(len(counts))]
    else:
        energias = [i * (ev_per_channel / 1000.0) for i in range(len(counts))]
    
    df = pd.DataFrame({
        'Energia_keV': energias,
        'Cuentas': counts
    })
    
    live_time = spectrum.get('live_time')
    if live_time is None:
        live_time = 0.0
    xray_voltage_kv = spectrum.get('xray_voltage_kv')
    if xray_voltage_kv is None:
        xray_voltage_kv = 0.0
    xray_filament_current = spectrum.get('xray_filament_current')
    if xray_filament_current is None:
        xray_filament_current = 0.0
        
    metadata = {
        'num_channels': num_channels,
        'ev_per_channel': ev_per_channel,
        'live_time': live_time,
        'xray_voltage_kv': xray_voltage_kv,
        'xray_filament_current': xray_filament_current,
        'version': header.get('version'),
        'file_type': header.get('file_type'),
        'nombre_archivo': os.path.basename(ruta_archivo)
    }
    
    return {
        'metadata': metadata,
        'datos': df
    }

def parsear_rtx(ruta_rtx):
    """
    Parsea el archivo XML .rtx de Artax.
    Retorna una lista de diccionarios con la jerarquía de cada espectro:
    [
      {
        'nombre': 'ANALYZE_EMP-7060@190526_141011',
        'archivo_pdz': 'ANALYZE_EMP-7060.pdz',
        'grupo_padre': 'Points Negro',
        'categorias': ['Points Oxtotitlan', 'Points Panel1_GrutaNorte', 'Points Negro']
      },
      ...
    ]
    """
    tree = ET.parse(ruta_rtx)
    root = tree.getroot()
    
    espectros = []
    
    def recorrer(element, ruta_actual):
        elem_type = element.attrib.get("Type", "")
        elem_name = element.attrib.get("Name", "")
        
        nueva_ruta = list(ruta_actual)
        
        if element.tag == "ClassInstance":
            if elem_type == "TRTSpectrum":
                # Limpiar el nombre para obtener el pdz potencial
                nombre_base = elem_name.split('@')[0]
                archivo_pdz = f"{nombre_base}.pdz"
                
                # Buscar metadatos descendientes
                live_time = 0.0
                xray_voltage_kv = 0.0
                xray_filament_current = 0.0
                channel_count = 2048
                calib_lin = 0.02
                sigma_abs = 0.0
                counts = []
                
                lt_elem = element.find('.//LifeTime')
                if lt_elem is not None and lt_elem.text:
                    try:
                        live_time = float(lt_elem.text) / 1000.0
                    except:
                        pass
                        
                hv_elem = element.find('.//HighVoltage')
                if hv_elem is not None and hv_elem.text:
                    try:
                        xray_voltage_kv = float(hv_elem.text)
                    except:
                        pass
                        
                tc_elem = element.find('.//TubeCurrent')
                if tc_elem is not None and tc_elem.text:
                    try:
                        xray_filament_current = float(tc_elem.text)
                    except:
                        pass
                        
                cc_elem = element.find('.//ChannelCount')
                if cc_elem is not None and cc_elem.text:
                    try:
                        channel_count = int(cc_elem.text)
                    except:
                        pass
                        
                cl_elem = element.find('.//CalibLin')
                if cl_elem is not None and cl_elem.text:
                    try:
                        calib_lin = float(cl_elem.text)
                    except:
                        pass
                        
                sa_elem = element.find('.//SigmaAbs')
                if sa_elem is not None and sa_elem.text:
                    try:
                        sigma_abs = float(sa_elem.text)
                    except:
                        pass
                        
                ch_elem = element.find('.//Channels')
                if ch_elem is not None and ch_elem.text:
                    try:
                        counts = [float(x) for x in ch_elem.text.split(',') if x.strip()]
                    except Exception as e:
                        print(f"Error parseando canales XML: {e}")
                
                espectros.append({
                    'nombre': elem_name,
                    'archivo_pdz': archivo_pdz,
                    'grupo_padre': ruta_actual[-1] if ruta_actual else '',
                    'categorias': nueva_ruta,
                    'xml_data': {
                        'live_time': live_time,
                        'xray_voltage_kv': xray_voltage_kv,
                        'xray_filament_current': xray_filament_current,
                        'ev_per_channel': calib_lin * 1000.0,
                        'num_channels': channel_count,
                        'xml_calib': (calib_lin, sigma_abs),
                        'counts': counts
                    }
                })
                return
            elif elem_type in ("TRTBase", "TRTProject"):
                if elem_name and elem_name != "RoentecProject":
                    nueva_ruta.append(elem_name)
                    
        for child in element:
            recorrer(child, nueva_ruta)
            
    recorrer(root, [])
    return espectros

def calcular_fondo_snip(counts, iteraciones=24):
    """
    Algoritmo SNIP (Statistics-sensitive Non-linear Iterative Peak-clipping)
    vectorizado para calcular el fondo continuo en espectros XRF.
    """
    counts = np.array(counts, dtype=float)
    y = np.log(counts + 1.0)
    n = len(y)
    z = np.copy(y)
    for p in range(1, iteraciones + 1):
        val = (y[:-2*p] + y[2*p:]) / 2.0
        z[p:-p] = np.minimum(z[p:-p], val)
        y = np.copy(z)
    return np.exp(y) - 1.0

def calcular_area_neta_pico(counts, fondo, index, window=7):
    """
    Calcula el área neta bajo un pico integrando las cuentas en una ventana
    alrededor del índice del pico y restando el fondo estimado.
    """
    counts = np.array(counts, dtype=float)
    fondo = np.array(fondo, dtype=float)
    
    start = max(0, index - window // 2)
    end = min(len(counts), index + window // 2 + 1)
    
    area_bruta = np.sum(counts[start:end])
    area_fondo = np.sum(fondo[start:end])
    area_neta = max(0.0, area_bruta - area_fondo)
    
    return area_bruta, area_neta

def buscar_picos(energias, counts, fondo, prominencia_min=None):
    """
    Busca picos significativos en el espectro XRF restando el fondo continuo.
    Calcula la intensidad neta y estima el área integrada bajo cada pico.
    Si prominencia_min es None, se calcula adaptativamente basándose en la raíz del fondo máximo.
    """
    from scipy.signal import find_peaks
    
    counts = np.array(counts, dtype=float)
    fondo = np.array(fondo, dtype=float)
    cuentas_netas = counts - fondo
    
    if prominencia_min is None or prominencia_min <= 0:
        # Calcular prominencia adaptativa basada en ruido Poisson (~ 3 * sqrt(max_fondo))
        max_fondo = np.max(fondo)
        prominencia_min = max(30.0, 3.0 * np.sqrt(max_fondo))
    
    # Encontrar índices de los picos
    picos_idx, propiedades = find_peaks(cuentas_netas, prominence=prominencia_min, distance=15)
    
    picos_info = []
    net_areas = []
    
    for idx in picos_idx:
        energia = energias[idx]
        elemento = identificar_elemento(energia)
        
        # Calcular áreas brutas y netas del pico
        bruta_area, neta_area = calcular_area_neta_pico(counts, fondo, idx)
        net_areas.append(neta_area)
        
        picos_info.append({
            'index': idx,
            'energia_kev': energia,
            'cuentas_brutas': counts[idx],
            'cuentas_netas': cuentas_netas[idx],
            'fondo': fondo[idx],
            'elemento': elemento,
            'area_bruta': bruta_area,
            'area_neta': neta_area,
            'area_relativa': 0.0  # Se calcula después
        })
        
    # Calcular áreas relativas porcentuales
    total_net_area = sum(net_areas)
    if total_net_area > 0:
        for p in picos_info:
            p['area_relativa'] = (p['area_neta'] / total_net_area) * 100.0
            
    return picos_info

def identificar_elemento(energia_kev, tolerancia_kev=0.12):
    """
    Identifica el elemento químico más probable para una energía de pico dada.
    """
    cercano = None
    min_diff = tolerancia_kev
    for elem, (ref_energy, line, label) in XRF_ELEMENTS.items():
        diff = abs(energia_kev - ref_energy)
        if diff < min_diff:
            min_diff = diff
            cercano = f"{label} {line}"
    return cercano

def calcular_pca_espectros(espectros_dict, canal_min=100, canal_max=1000, metodo='covarianza', alinear_signos=True):
    """
    Realiza un Análisis de Componentes Principales (PCA) en la matriz de espectros
    utilizando Descomposición en Valores Singulares (SVD) sobre NumPy.
    Soporta métodos de 'covarianza' (solo centrado) y 'correlacion' (centrado y estandarizado).
    Permite alineación de signos determinista para consistencia visual.
    """
    item_ids = list(espectros_dict.keys())
    if len(item_ids) < 3:
        return None
        
    matrix = []
    names = []
    categories = []
    expected_len = canal_max - canal_min
    
    for item_id, esp in espectros_dict.items():
        counts = esp['datos']['Cuentas'].values
        roi_counts = counts[canal_min:canal_max]
        if len(roi_counts) < expected_len:
            pad_width = expected_len - len(roi_counts)
            roi_counts = np.pad(roi_counts, (0, pad_width), 'constant')
        matrix.append(roi_counts)
        names.append(esp['metadata']['nombre_archivo'])
        
        # Obtener grupo o material (Negro, Rojo, Ocre, etc.)
        cat = esp.get('grupo_padre', 'Sin clasificar').replace("Points ", "")
        categories.append(cat)
        
    X = np.array(matrix, dtype=float)
    
    # Normalizar por el área de cada espectro en la ROI para evitar diferencias por tiempo de disparo
    row_sums = X.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    X_normalized = X / row_sums
    
    # Centrar datos normalizados
    mean = np.mean(X_normalized, axis=0)
    X_centered = X_normalized - mean
    
    if metodo == 'correlacion':
        std = np.std(X_normalized, axis=0)
        std[std == 0] = 1.0 # Evitar división por cero
        X_centered = X_centered / std
    
    try:
        # SVD sobre datos transformados
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
        
        # Alinear signos de forma determinista para consistencia
        if alinear_signos:
            for j in range(Vt.shape[0]):
                max_abs_idx = np.argmax(np.abs(Vt[j]))
                if Vt[j, max_abs_idx] < 0:
                    Vt[j] = -Vt[j]
        
        # Proyectar sobre los primeros 2 componentes principales
        PC_coords = np.dot(X_centered, Vt[:2].T)
        
        # Calcular varianza explicada
        var_explicada = (S ** 2) / np.sum(S ** 2)
        var_pc1 = var_explicada[0] * 100
        var_pc2 = var_explicada[1] * 100
        
        resultados = []
        for i, item_id in enumerate(item_ids):
            resultados.append({
                'item_id': item_id,
                'nombre': names[i],
                'categoria': categories[i],
                'pc1': PC_coords[i, 0],
                'pc2': PC_coords[i, 1]
            })
            
        return {
            'resultados': resultados,
            'var_pc1': var_pc1,
            'var_pc2': var_pc2
        }
    except Exception as e:
        print(f"Error calculando PCA: {e}")
        return None

def ruteador_de_archivos(lista_archivos):
    """
    Recibe una lista de archivos (.pdz, .rtx, etc.) cargados en la GUI.
    Decide cómo enrutar el procesamiento de cada tipo de archivo.
    """
    print(f"\n[Ruteador] Procesando {len(lista_archivos)} archivo(s)...")
    for ruta in lista_archivos:
        ext = os.path.splitext(ruta)[1].lower()
        nombre = os.path.basename(ruta)
        
        if ext == '.pdz':
            try:
                res = leer_pdz(ruta)
                meta = res['metadata']
                print(f"  [PDZ] Leído '{nombre}' con éxito: {meta['num_channels']} canales, {meta['live_time']:.2f}s tiempo vivo.")
            except Exception as e:
                print(f"  [PDZ ERROR] No se pudo leer '{nombre}': {e}")
                
        elif ext == '.rtx':
            try:
                espectros = parsear_rtx(ruta)
                print(f"  [RTX] Leído '{nombre}' con éxito. Encontrados {len(espectros)} espectros en la jerarquía:")
                for esp in espectros[:3]:
                    print(f"    - Espectro: {esp['nombre']} -> Jerarquía: {' > '.join(esp['categorias'])}")
                if len(espectros) > 3:
                    print(f"    - ... y {len(espectros) - 3} más.")
            except Exception as e:
                print(f"  [RTX ERROR] No se pudo leer '{nombre}': {e}")
        else:
            print(f"  [INFO] Archivo con extensión no soportada directamente: '{nombre}' ({ext})")

def sugerir_pigmentos(elementos_detectados):
    """
    Recibe una lista de elementos (que pueden ser tuplas (nombre, porcentaje) o strings)
    y sugiere pigmentos históricos y compuestos arqueológicos asociados, incluyendo
    los porcentajes de intensidad de cada elemento.
    Retorna una lista de diccionarios con la sugerencia, el color y la justificación.
    """
    simbolos_pct = {}
    for item in elementos_detectados:
        if isinstance(item, tuple) and len(item) == 2:
            el, pct = item
        elif isinstance(item, dict):
            el = item.get('elemento')
            pct = item.get('porcentaje')
        else:
            el = item
            pct = None
            
        if el is None:
            continue
            
        # Extraer símbolo si viene en formato "Hierro (Fe) Kα" o similar
        if '(' in el and ')' in el:
            sym = el.split('(')[1].split(')')[0].strip()
        else:
            sym = str(el).strip()
            
        if pct is not None:
            simbolos_pct[sym] = simbolos_pct.get(sym, 0.0) + float(pct)
        else:
            if sym not in simbolos_pct:
                simbolos_pct[sym] = None
            
    simbolos = set(simbolos_pct.keys())
    sugerencias = []
    
    # 1. Vermellón / Cinabrio (Rojo)
    if 'Hg' in simbolos:
        pct = simbolos_pct.get('Hg')
        pct_str = f" [{pct:.2f}%]" if pct is not None else ""
        sugerencias.append({
            'pigmento': f'Bermellón / Cinabrio (HgS){pct_str}',
            'color': 'Rojo',
            'justificacion': 'Presencia de Mercurio (Hg). Indicador físico y químico inequívoco de bermellón.'
        })
        
    # 2. Amarillo de Plomo-Estaño
    if 'Pb' in simbolos and 'Sn' in simbolos:
        pct_pb = simbolos_pct.get('Pb')
        pct_sn = simbolos_pct.get('Sn')
        pct_str = f" [Pb: {pct_pb:.2f}%, Sn: {pct_sn:.2f}%]" if (pct_pb is not None and pct_sn is not None) else ""
        sugerencias.append({
            'pigmento': f'Amarillo de Plomo-Estaño (Pb2SnO4 o PbSn1-xSixO3){pct_str}',
            'color': 'Amarillo',
            'justificacion': 'Coincidencia de Plomo (Pb) y Estaño (Sn). Típico de pinturas renacentistas.'
        })
        
    # 3. Verde Esmeralda (París) o mezclas
    if 'Cu' in simbolos and 'As' in simbolos:
        pct_cu = simbolos_pct.get('Cu')
        pct_as = simbolos_pct.get('As')
        pct_str = f" [Cu: {pct_cu:.2f}%, As: {pct_as:.2f}%]" if (pct_cu is not None and pct_as is not None) else ""
        sugerencias.append({
            'pigmento': f'Verde Esmeralda / Verde de París (Cu-As){pct_str}',
            'color': 'Verde',
            'justificacion': 'Coincidencia de Cobre (Cu) y Arsénico (As). Típico de formulaciones del siglo XIX o mezclas intencionales.'
        })
        
    # 4. Oropimente o Realgar
    if 'As' in simbolos and 'Cu' not in simbolos:
        pct = simbolos_pct.get('As')
        pct_str = f" [{pct:.2f}%]" if pct is not None else ""
        sugerencias.append({
            'pigmento': f'Oropimente (As2S3) o Realgar (As4S4){pct_str}',
            'color': 'Amarillo o Rojo/Naranja',
            'justificacion': 'Presencia de Arsénico (As) sin Cobre. Oropimente (amarillo) y Realgar (rojo) son pigmentos de arsénico muy comunes en manuscritos y arte rupestre prehispánico.'
        })
        
    # 5. Cobre solo (Azurita, Malaquita, Cardenillo)
    if 'Cu' in simbolos and 'As' not in simbolos:
        pct = simbolos_pct.get('Cu')
        pct_str = f" [{pct:.2f}%]" if pct is not None else ""
        sugerencias.append({
            'pigmento': f'Azurita (Azul), Malaquita (Verde), Cardenillo (Verde) o Resinato de Cobre{pct_str}',
            'color': 'Azul o Verde',
            'justificacion': 'Presencia de Cobre (Cu). Indica compuestos de cobre carbonatados o acetatos.'
        })
        
    # 6. Sombra (Umber) o Tierras
    if 'Fe' in simbolos and 'Mn' in simbolos:
        pct_fe = simbolos_pct.get('Fe')
        pct_mn = simbolos_pct.get('Mn')
        pct_str = f" [Fe: {pct_fe:.2f}%, Mn: {pct_mn:.2f}%]" if (pct_fe is not None and pct_mn is not None) else ""
        sugerencias.append({
            'pigmento': f'Tierra de Sombra (Umber) / Ocre con Manganeso{pct_str}',
            'color': 'Café / Marrón',
            'justificacion': 'Coincidencia de Hierro (Fe) y Manganeso (Mn). Tierra arcillosa rica en óxidos de Fe y Mn.'
        })
    elif 'Fe' in simbolos:
        pct = simbolos_pct.get('Fe')
        pct_str = f" [{pct:.2f}%]" if pct is not None else ""
        sugerencias.append({
            'pigmento': f'Ocres / Tierras de Hierro (Hematita o Goethita){pct_str}',
            'color': 'Rojo, Amarillo o Café / Marrón',
            'justificacion': 'Presencia dominante de Hierro (Fe). Típico de Hematita (rojo), Goethita (amarillo) o Limonita.'
        })
        
    # 6.5 Negros Minerales y de Hueso
    if 'P' in simbolos and 'Ca' in simbolos:
        pct_ca = simbolos_pct.get('Ca')
        pct_p = simbolos_pct.get('P')
        pct_str = f" [Ca: {pct_ca:.2f}%, P: {pct_p:.2f}%]" if (pct_ca is not None and pct_p is not None) else ""
        sugerencias.append({
            'pigmento': f'Negro de Hueso o de Marfil (Fosfato de Calcio){pct_str}',
            'color': 'Negro',
            'justificacion': 'Coincidencia de Fósforo (P) y Calcio (Ca). Indica un pigmento carbonizado de origen animal.'
        })
    if 'Mn' in simbolos and 'Fe' not in simbolos:
        pct = simbolos_pct.get('Mn')
        pct_str = f" [{pct:.2f}%]" if pct is not None else ""
        sugerencias.append({
            'pigmento': f'Negro de Manganeso (Óxidos de Mn / Pirolusita){pct_str}',
            'color': 'Negro / Oscuro',
            'justificacion': 'Presencia de Manganeso (Mn) sin Hierro. Típico de pigmentos negros minerales en arte rupestre.'
        })
        
    # 7. Plomo solo (Blanco de Plomo o Minio)
    if 'Pb' in simbolos and 'Sn' not in simbolos:
        pct = simbolos_pct.get('Pb')
        pct_str = f" [{pct:.2f}%]" if pct is not None else ""
        sugerencias.append({
            'pigmento': f'Blanco de Plomo (2PbCO3·Pb(OH)2) o Minio (Pb3O4){pct_str}',
            'color': 'Blanco o Rojo',
            'justificacion': 'Presencia de Plomo (Pb) sin Estaño. Puede corresponder a Blanco de Plomo (soportes/mezclas) o Minio (rojo plomo).'
        })
        
    # 8. Yeso
    if 'Ca' in simbolos and 'S' in simbolos:
        pct_ca = simbolos_pct.get('Ca')
        pct_s = simbolos_pct.get('S')
        pct_str = f" [Ca: {pct_ca:.2f}%, S: {pct_s:.2f}%]" if (pct_ca is not None and pct_s is not None) else ""
        sugerencias.append({
            'pigmento': f'Yeso (CaSO4·2H2O){pct_str}',
            'color': 'Blanco (Preparación)',
            'justificacion': 'Coincidencia de Calcio (Ca) y Azufre (S). Típico de bases de preparación (gesso) o consolidación.'
        })
    elif 'Ca' in simbolos:
        pct = simbolos_pct.get('Ca')
        pct_str = f" [{pct:.2f}%]" if pct is not None else ""
        sugerencias.append({
            'pigmento': f'Calcita / Tiza (CaCO3) o Yeso{pct_str}',
            'color': 'Blanco (Carga / Soporte)',
            'justificacion': 'Presencia de Calcio (Ca). Utilizado como base de preparación, soporte pétreo o carga blanca.'
        })
        
    # 9. Blanco de Titanio o Blanco de Zinc (Modernos)
    if 'Ti' in simbolos and 'Fe' not in simbolos:  # Si hay Fe, Ti suele ser arcilla mineral incidental
        pct = simbolos_pct.get('Ti')
        pct_str = f" [{pct:.2f}%]" if pct is not None else ""
        sugerencias.append({
            'pigmento': f'Blanco de Titanio (TiO2){pct_str}',
            'color': 'Blanco (Moderno)',
            'justificacion': 'Presencia de Titanio (Ti) sin Hierro. Indica una formulación moderna (s. XX) o restauración.'
        })
    if 'Zn' in simbolos:
        pct = simbolos_pct.get('Zn')
        pct_str = f" [{pct:.2f}%]" if pct is not None else ""
        sugerencias.append({
            'pigmento': f'Blanco de Zinc (ZnO){pct_str}',
            'color': 'Blanco (Moderno)',
            'justificacion': 'Presencia de Zinc (Zn). Indica formulación moderna (s. XIX-XX) o restauración.'
        })
        
    # 10. Picos del haz del XRF (Rodio y Paladio)
    if 'Rh' in simbolos or 'Pd' in simbolos:
        pct_rh = simbolos_pct.get('Rh')
        pct_pd = simbolos_pct.get('Pd')
        elements_present = []
        if pct_rh is not None: elements_present.append(f"Rh: {pct_rh:.2f}%")
        if pct_pd is not None: elements_present.append(f"Pd: {pct_pd:.2f}%")
        pct_str = f" [{', '.join(elements_present)}]" if elements_present else ""
        sugerencias.append({
            'pigmento': f'Haz del Tubo XRF (Rodio / Paladio) [Artefacto]{pct_str}',
            'color': 'Ninguno',
            'justificacion': 'Picos originados por la dispersión del haz del propio tubo de rayos X (anodo de Rh o Pd). Deben ser ignorados como pigmentos.'
        })
        
    return sugerencias

def estimar_porcentajes_compuestos(picos):
    """
    Estima el porcentaje de compuestos (pigmentos o bases de preparación)
    en la muestra a partir de las áreas netas relativas de los picos.
    Retorna una lista de diccionarios ordenados de mayor a menor:
      [ {'compuesto': 'Ocres / Tierras de Hierro', 'porcentaje': 45.2}, ... ]
    """
    # Agrupar áreas por símbolo químico de elemento
    areas = {}
    for p in picos:
        el = p.get('elemento')
        if not el:
            continue
        # Extraer símbolo químico entre paréntesis, ej: "Hierro (Fe) Ka" -> "Fe"
        if '(' in el and ')' in el:
            sym = el.split('(')[1].split(')')[0].strip()
        else:
            sym = str(el).strip()
        
        areas[sym] = areas.get(sym, 0.0) + p.get('area_relativa', 0.0)
    
    compuestos = {}
    
    # 1. Bermellón / Cinabrio (HgS) -> basado en Hg
    if 'Hg' in areas:
        compuestos['Bermellón / Cinabrio (HgS)'] = areas['Hg']
        
    # 2. Amarillo de Plomo-Estaño (Pb-Sn) -> basado en Sn
    if 'Sn' in areas:
        compuestos['Amarillo de Plomo-Estaño'] = areas['Sn']
        
    # 3. Verde Esmeralda (Cu-As) -> si hay Cu y As
    if 'Cu' in areas and 'As' in areas:
        val = areas['Cu'] + areas['As']
        compuestos['Verde Esmeralda (París)'] = val
        # Consumimos Cu y As para evitar duplicar en Malaquita/Oropimente
        try:
            del areas['Cu']
        except KeyError:
            pass
        try:
            del areas['As']
        except KeyError:
            pass
        
    # 4. Oropimente / Realgar (As2S3 / As4S4) -> si queda As
    if 'As' in areas:
        compuestos['Oropimente / Realgar (As)'] = areas['As']
        
    # 5. Azurita / Malaquita / Cardenillo -> si queda Cu
    if 'Cu' in areas:
        compuestos['Malaquita / Azurita / Cardenillo (Cu)'] = areas['Cu']
        
    # 6. Esmalte (Cobalto) -> Co
    if 'Co' in areas:
        compuestos['Esmalte (Smalt)'] = areas['Co']
        
    # 7. Tierra de Sombra (Umber) -> si hay Fe y Mn
    if 'Fe' in areas and 'Mn' in areas:
        val = areas['Fe'] + areas['Mn']
        compuestos['Tierra de Sombra (Hierro + Manganeso)'] = val
        try:
            del areas['Fe']
        except KeyError:
            pass
        try:
            del areas['Mn']
        except KeyError:
            pass
        
    # 8. Ocres / Tierras de Hierro -> si queda Fe
    if 'Fe' in areas:
        compuestos['Ocres / Tierras de Hierro (Hematita/Goethita)'] = areas['Fe']
        
    # 9. Negro de Hueso / Marfil (Ca-P) -> si hay P
    if 'P' in areas:
        compuestos['Negro de Hueso (Fosfato de Calcio)'] = areas['P']
        # Si hay Ca, reducimos el área de Ca proporcionalmente
        if 'Ca' in areas:
            areas['Ca'] = max(0.0, areas['Ca'] - 1.5 * areas['P'])
            
    # 10. Negro de Manganeso -> si queda Mn
    if 'Mn' in areas:
        compuestos['Negro de Manganeso (Óxidos de Mn)'] = areas['Mn']
        
    # 11. Yeso (CaSO4) -> si hay S y Ca
    if 'S' in areas:
        compuestos['Yeso (CaSO4)'] = areas['S']
        if 'Ca' in areas:
            # Reducimos Ca proporcionalmente al yeso (relación 1:1)
            areas['Ca'] = max(0.0, areas['Ca'] - areas['S'])
            
    # 12. Calcita / Tiza / Cal (CaCO3) o soporte calcáreo -> si queda Ca
    if 'Ca' in areas and areas['Ca'] > 0.0:
        compuestos['Calcita / Tiza / Soporte Calizo'] = areas['Ca']
        
    # 13. Blanco de Plomo (sólo Pb)
    if 'Pb' in areas:
        pb_val = areas['Pb']
        if 'Sn' in compuestos:
            pb_val = max(0.0, pb_val - 2.0 * compuestos['Amarillo de Plomo-Estaño'])
        if pb_val > 0.0:
            compuestos['Blanco de Plomo / Minio (Pb)'] = pb_val
            
    # 14. Blanco de Titanio -> moderno Ti (sin Fe)
    if 'Ti' in areas:
        compuestos['Blanco de Titanio (TiO2)'] = areas['Ti']
        
    # 15. Blanco de Zinc -> moderno Zn
    if 'Zn' in areas:
        compuestos['Blanco de Zinc (ZnO)'] = areas['Zn']
        
    # Sumar total de compuestos detectados
    total_compuestos = sum(compuestos.values())
    
    if total_compuestos == 0:
        return []
        
    # Normalizar los porcentajes para que sumen 100%
    resultados = []
    for comp, val in compuestos.items():
        pct = (val / total_compuestos) * 100.0
        if pct >= 0.5:
            resultados.append({
                'compuesto': comp,
                'porcentaje': pct
            })
            
    # Ordenar de mayor a menor porcentaje
    resultados.sort(key=lambda x: x['porcentaje'], reverse=True)
    return resultados

