import streamlit as st
import math
from pathlib import Path

st.set_page_config(page_title="Banco de tubos", layout="wide")

# Esto es para quitar el espacio de arriba del título
st.markdown("""
<style>
    /* Quita espacio superior del contenido principal */
    .block-container {
        padding-top: 0.8rem;
    }

    /* Quita espacio superior de la barra lateral */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)


# Se usa para encontrar imágenes del proyecto
BASE_DIR = Path(__file__).parent
IMG_ALINEADOS = BASE_DIR / "Tubos_alineados.png"
IMG_ESCALONADOS = BASE_DIR / "Tubos_escalonados.png"

st.title("Banco de tubos")

# Barra lateral de la página
with st.sidebar:
    st.markdown("## Configuración del banco")
    st.caption("Seleccione las características del banco de tubos 🛠️")
    st.divider()

    st.sidebar.markdown("#### Tipo de arreglo")
    Tipo_banco = st.selectbox(
        "Tipo de banco", 
        ["Seleccione una opción","Alineado", "Escalonado"]
    )

    st.markdown("#### Esquema")
    if Tipo_banco == "Escalonado":
        st.image(IMG_ESCALONADOS, use_container_width=True)
    elif Tipo_banco == "Alineado":
        st.image(IMG_ALINEADOS, use_container_width=True)
    else:
        st.info("Seleccione un tipo de banco para ver el esquema")

    Relación_pasos = st.selectbox(
        "Relación de pasos", 
        [
            "Seleccione una opción", 
            "SL = ST",
            "SL ≠ ST" 
            ] 
        )
    
    st.divider()
    st.markdown("#### Temperatura conocida del fluido")
    st.caption("Fluido que circula externamente por el banco de tubos.")

    Temp_fluido = st.selectbox(
        "Temperatura",
        [
            "Seleccione una opción",
            "Temperatura de entrada Ti",
            "Temperatura de salida Te"
            ]
        )

    st.divider()
    st.markdown("#### Condensación dentro del tubo")
    Condensacion = st.selectbox(
        "¿Hay flujo másico condensado dentro de la tubería?",
        [
            "Seleccione una opción",
            "Sí",
            "No"
            ]
        )
    
    st.divider()
    st.caption("Proyecto final de transferencia de calor. Programa de banco de tubos. Presentado por Valerie Obregón.")


# Formulario (Sirve para que se calcule todo cuando le dan click al botón Calcular y no cada que ingresa un dato)
with st.form("Datos"):
    st.subheader("Datos 📝")

    c1, c2 = st.columns(2)

    # La primera columna es la de propiedades
    with c1:
        st.markdown("### Propiedades del fluido 🧪")
        # Si quiero mejor poner campos en blanco debo usar text_input (queda vacío)
        rho_txt = st.text_input("Densidad ρ (kg/m³)", placeholder="Ej: 1.2")
        miu_txt  = st.text_input("Viscosidad dinámica μ (Pa·s)", placeholder="Ej: 1.8e-5")
        k_txt   = st.text_input("Conductividad térmica k (W/m·K)", placeholder="Ej: 0.026")
        Cp_txt = st.text_input("Calor específico Cp (kJ/kg·K)", placeholder="Ej: 1.007")
        Pr_txt = st.text_input(
            r"Prandtl $Pr$",
            placeholder="Ej: 0.71"
            )
        Prs_txt = st.text_input(
            r"Prandtl en superficie $Pr_s$",
            placeholder="Ej: 0.71"
            )
        v_txt   = st.text_input("Velocidad media v (m/s)", placeholder="Ej: 2.0")
        
        # Temperatura del fluido que circula externamente por los tubos.
        if Temp_fluido == "Temperatura de entrada Ti":
            Ti_txt = st.text_input(
                r"Temperatura de entrada del fluido $T_i$ (°C)",
            placeholder="Ej: 27"
            )
            Te_txt = ""
        elif Temp_fluido == "Temperatura de salida Te":
            Te_txt = st.text_input(
                r"Temperatura de salida del fluido $T_e$ (°C)",
                placeholder="Ej: 27"
            )
            Ti_txt = ""
        else:
            st.info("Seleccione en la barra lateral qué temperatura del fluido es conocida.")
            Ti_txt = ""
            Te_txt = ""
        
        hfg_txt = ""
        if Condensacion == "Sí":
            hfg_txt = st.text_input(
                r"Entalpía de vaporización $h_{fg}$ (kJ/kg)",
                placeholder="Ej: 2257"
            )
        elif Condensacion == "Seleccione una opción":
            st.info("Seleccione en la barra lateral si hay condensación (Sí/No)")

    # La segunda columna es la de las dimensiones
    with c2:
        st.markdown("### Dimensiones 📐")
        D_txt  = st.text_input("Diámetro del tubo D (m)", placeholder="Ej: 0.025")
        ST_txt = st.text_input(
            r"Paso transversal $S_T$ (m)",
            placeholder="Ej: 0.05"
            )
        SL_txt = st.text_input(
            r"Paso longitudinal $S_L$ (m)",
            placeholder="Ej: 0.06"
            )
        L_txt  = st.text_input("Longitud del tubo L (m)", placeholder="Ej: 1.0")
        NL_txt = st.text_input(
            r"Número de tubos en plano longitudinal $N_L$",
            placeholder="Ej: 5 (Ingresar número entero)"
            )
        NT_txt = st.text_input(
            r"Número de tubos en plano transversal $N_T$",
            placeholder="Ej: 8 (Ingresar número entero)"
            )
        Ts_txt = st.text_input(
            r"Temperatura superficial $T_S$ (°C)",
            placeholder="Ej: 110"
            )

    calcular = st.form_submit_button("Calcular")

# Cálculos

# Revisa si está vacía alguna casilla de datos, y si falta algo lanza error.
# Todos los datos que vienen del formulario de arribita pasan por aquí
def to_float(name, s):
    if s.strip() == "":
        raise ValueError(f"Falta el dato: {name}")
    return float(s)

# Cuando le dan al botón de calcular se ejecuta.
if calcular:
        # Todo lo que son los cálculos va dentro del try.
    try:
        if Relación_pasos == "Seleccione una opción":
            st.error("Debe seleccionar la relación de pasos.")
            st.stop()
            
        if Tipo_banco == "Seleccione una opción":
            st.error("Debe seleccionar el tipo de banco.")
            st.stop()
            
        if Temp_fluido == "Seleccione una opción":
            st.error("Debe seleccionar qué temperatura del fluido es conocida (Ti o Te).")
            st.stop()
        
        if Condensacion == "Seleccione una opción":
            st.error("Debe seleccionar si hay flujo másico condensado dentro de la tubería (Sí o No).")
            st.stop()
  
        # Aquí los datos que ingresaron se convierten en número para los cálculos.
        
        rho = to_float("ρ", rho_txt)
        miu = to_float("μ", miu_txt)
        k   = to_float("k", k_txt)
        Cp = to_float("Cp", Cp_txt)
        Pr  = to_float("Pr", Pr_txt)
        Prs = to_float("Prs", Prs_txt)
        v   = to_float("v", v_txt)
        
        if Temp_fluido == "Temperatura de entrada Ti":
            Ti  = to_float("Ti", Ti_txt)
            Te = None
        else:
            Te = to_float("Te", Te_txt)
            Ti = None

        if Condensacion == "Sí":
            hfg = to_float("hfg", hfg_txt)
        else:
            hfg = None
        
        D   = to_float("D", D_txt)
        ST  = to_float("ST", ST_txt)
        SL  = to_float("SL", SL_txt)
        L   = to_float("L", L_txt)
        Ts  = to_float("Ts", Ts_txt)
        
        # Se agrega int para forzar que sea un número entero. No existen 3.7, o son 3 o 4 tubos. El 5.0 sigue siendo decimal.
        NL = int(to_float("NL", NL_txt))
        NT = int(to_float("NT", NT_txt))
        N  = NL * NT
        A1 = ST * L

        # ST debe ser mayor que D porque sino se chocan los tubos.
        if ST <= D:
            st.error("Debe cumplirse ST > D.")
            st.stop()

        # Cálculo del SD
        if Tipo_banco == "Alineado" and Relación_pasos == "SL = ST":
            SD = math.sqrt(SL**2 + SL**2)
        elif Tipo_banco == "Alineado" and Relación_pasos == "SL ≠ ST":
            SD = math.sqrt(SL**2 + ST**2)
        elif Tipo_banco == "Escalonado" and Relación_pasos == "SL = ST":
            SD = math.sqrt((SL / 2)**2 + SL**2)
        elif Tipo_banco == "Escalonado" and Relación_pasos == "SL ≠ ST":
            SD = math.sqrt((ST / 2)**2 + SL**2)
        else:
            st.error("Tipo de banco o relación de pasos no seleccionado.")
            st.stop()

        # Áreas para escalonado
        A2 = (ST - D) * L
        A3 = 2 * (SD - D) * L
        
        # Vmáx a partir del caso
        if Tipo_banco == "Alineado":
            v_max = v * ST / (ST - D)
            vmax_label = "Vmáx"
        elif Tipo_banco == "Escalonado":
            if A2 < A3:
                v_max = v * ST / (ST - D)
                vmax_label = "Vmáx (V2)"
            else:
                v_max = v * ST / (2 * (SD - D))
                vmax_label = "Vmáx (V3)"
        else:
            st.error("Tipo de banco no reconocido.")
            st.stop()

        # Número de Reynolds
        Re = rho * v_max * D / miu

        # Correlaciones Nusselt
        if Tipo_banco == "Alineado":
            if 0 <= Re < 100:
                NuD = 0.9 * (Re**0.4) * (Pr**0.36) * ((Pr/Prs)**0.25)
                rango = "0–100"
            elif 100 <= Re < 1000:
                NuD = 0.52 * (Re**0.5) * (Pr**0.36) * ((Pr/Prs)**0.25)
                rango = "100–1000"
            elif 1000 <= Re < 2e5:
                NuD = 0.27 * (Re**0.63) * (Pr**0.36) * ((Pr/Prs)**0.25)
                rango = "1000–2×10^5"
            elif 2e5 <= Re <= 2e6:
                NuD = 0.033 * (Re**0.8) * (Pr**0.4) * ((Pr/Prs)**0.25)
                rango = "2×10^5–2×10^6"
            else:
                # Se usa warning porque avisa y deja continuar el cálculo, 
                # mientras que st.error marca error y detiene el cálculo.
                st.warning("Re está fuera del rango de validez de la correlación.")
                NuD = 0.033 * (Re**0.8) * (Pr**0.4) * ((Pr/Prs)**0.25)
                rango = "Fuera del rango de correlación"
            
        elif Tipo_banco == "Escalonado":
            if 0 <= Re < 500:
                NuD = 1.04 * (Re**0.4) * (Pr**0.36) * ((Pr/Prs)**0.25)
                rango = "0–500"
            elif 500 <= Re < 1000:
                NuD = 0.71 * (Re**0.5) * (Pr**0.36) * ((Pr/Prs)**0.25)
                rango = "500–1000"
            elif 1000 <= Re < 2e5:
                NuD = 0.35 * ((ST/SL)**0.2) * (Re**0.6) * (Pr**0.36) * ((Pr/Prs)**0.25)
                rango = "1000–2×10^5"
            elif 2e5 <= Re <= 2e6:
                NuD = 0.031 * ((ST/SL)**0.2) * (Re**0.8) * (Pr**0.36) * ((Pr/Prs)**0.25)
                rango = "2×10^5–2×10^6"
            else:
                st.warning("Re está fuera del rango de validez de la correlación.")
                NuD = 0.031 * ((ST/SL)**0.2) * (Re**0.8) * (Pr**0.36) * ((Pr/Prs)**0.25)
                rango = "Fuera del rango de correlación"
        
        else:
            st.error("Tipo de banco no reconocido. Seleccione Alineado o Escalonado.")
            st.stop()

        # Factor de corrección
        # Función para el factor de corrección
        def F_correccion(NL, Tipo_banco):
            if NL >= 16:
                return 1.0
        
            # Lista de NL en tablita de factor de corrección
            NL_valores = [1, 2, 3, 4, 5, 7, 10, 13]
            
            if Tipo_banco == "Alineado":
                F_valores = [0.70, 0.80, 0.86, 0.90, 0.93, 0.96, 0.98, 0.99]
            else:  # Escalonado
                F_valores = [0.64, 0.76, 0.84, 0.89, 0.93, 0.96, 0.98, 0.99]              
        
            # NL_cercano se usa cuando NL real no está en la tabla, ejemplo, NL = 6. 
            # El idx busca la posición de ese NL y el F_valores[idx]] me da el F correspondiente.
            NL_cercano = min(NL_valores, key=lambda x: abs(x - NL))
            idx = NL_valores.index(NL_cercano)
            return F_valores[idx]

        # luego de calcular NuD:
        if Re > 1000:
            F = F_correccion(NL, Tipo_banco)
        else:
            F = 1.0
            
        Nu = F * NuD        
        h = Nu * k / D
        A = math.pi * D * L * N
        m_dot = rho * v * A1 * NT      #kg/s
        
        # Cálculo de la temperatura desconocida
        Cp_J = Cp * 1000        # Pasa de kJ/kg·K a J/kg·K
        ash = h * A / (m_dot * Cp_J)       
        if Ti is not None:  # Dan Ti, hallar Te
            Ti_calc = Ti
            Te_calc = Ts - (Ts - Ti) * math.exp(-ash)
        else:               # Dan Te, hallar Ti
            Te_calc = Te
            Ti_calc = Ts - (Ts - Te) * math.exp(ash)

        # Cálculo del calor
        Q_dot = abs(m_dot * Cp * (Te_calc - Ti_calc))   #kW
        
        # Cálculo de flujo másico condensado
        if Condensacion == "Sí":
            m_cond = Q_dot / hfg    #kg/s
        else:
            m_cond = None
        
        # Resultados
        st.subheader("Resultados")
        if Temp_fluido == "Temperatura de entrada Ti":
            Temp_label = r"Temperatura de salida $T_e$ (°C)"
            Temp_value = Te_calc
        else:
            Temp_label = r"Temperatura de entrada $T_i$ (°C)"
            Temp_value = Ti_calc
            
        # Primera fila
        r1, r2 = st.columns(2)
        with r1:
            if vmax_label == "Vmáx (V2)":
                v_label = r"$V_{\max,2}$"
            else:
                v_label = r"$V_{\max}$"
            st.text_input(
                rf"Velocidad máxima {v_label} (m/s)",
                value=f"{v_max:.2f}",
                disabled=True
            )

            st.text_input(
                r"Número de Reynolds $Re$",
                value=f"{Re:.0f}  |  Rango: {rango}",
                disabled=True
            )
            st.text_input(
                r"Número de Nusselt $Nu$",
                value=f"{Nu:.2f}",
                disabled=True
            )
        with r2:
            st.text_input(
                r"Coeficiente convectivo $h$ (W/m$^2$·K)",
                value=f"{h:.2f}",
                disabled=True
            )
            st.text_input(
                Temp_label,
                value=f"{Temp_value:.2f}",
                disabled=True
            )
            st.text_input(
                r"Calor transferido $\dot{Q}$ (kW)",
                value=f"{Q_dot:.2f}",
                disabled=True
            )
        
        if Condensacion == "Sí":
            st.text_input(
                r"Masa de condensación $\dot{m}_{cond}$ (kg/s)",
                value=f"{m_cond:.4f}",
                disabled=True
            )

    except ValueError as e:
        st.error(str(e))
    except Exception:
        st.error("Hay un dato inválido. Usa solo números y punto decimal (ej: 0.71, 1.8e-5).")

 # Para correr el programa 
 # py -3.13 -m streamlit run streamlit_banco_de_tubos.py