import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
from math import pi
import streamlit as st

# Basic Font Settings
plt.rcParams["font.family"] = "DejaVu Sans"  # Universal font support
plt.rcParams["axes.unicode_minus"] = False

# Streamlit Configuration
st.set_page_config(
    page_title="AP Chemistry: 치아 법랑질 부식의 원인과 이의 대처 방안에 대한 산 염기 반응 중심의 관찰 및 탐구",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)


def plot_ph_solubility():
    """
    Visualization 1: pH vs Solubility Curve (Critical pH Analysis)
    Demonstrates why erosion occurs below pH 5.5 and the stability of the new material.
    """
    ph_values = np.linspace(3, 8, 100)

    # Solubility Models
    # Hydroxyapatite: High sensitivity to acid (Critical pH ~5.5)
    solubility_hap = 10 ** (5.5 - ph_values)
    # New Material / Fluorapatite: Enhanced stability (Critical pH ~4.5)
    solubility_new = 10 ** (4.5 - ph_values)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plotting
    ax.plot(
        ph_values,
        solubility_hap,
        label="Hydroxyapatite",
        color="#ff4b4b",
        linewidth=3,
    )
    ax.plot(
        ph_values,
        solubility_new,
        label="Fluorapatite",
        color="#1f77b4",
        linestyle="--",
        linewidth=3,
    )

    # Annotations
    ax.axvline(x=5.5, color="gray", linestyle=":", alpha=0.8)
    ax.text(5.55, 60, "Critical pH (5.5)\nNormal Enamel", fontsize=10, color="#333")

    ax.axvline(x=4.5, color="gray", linestyle=":", alpha=0.8)
    ax.text(4.55, 20, "Enhanced Stability\n(pH 4.5)", fontsize=10, color="#1f77b4")

    # Styling
    ax.set_title(
        "Solubility vs. pH: Stability Range Expansion", fontsize=14, fontweight="bold"
    )
    ax.set_xlabel("pH Level", fontsize=12)
    ax.set_ylabel("Relative Solubility", fontsize=12)
    ax.set_xlim(8, 3)  # Reverse axis: Basic -> Acidic
    ax.set_ylim(0, 100)

    # Fill the "Danger Zone"
    ax.fill_between(
        ph_values,
        0,
        100,
        where=(ph_values <= 5.5),
        color="red",
        alpha=0.1,
        label="Erosion Zone",
    )

    ax.fill_between(
        ph_values,
        0,
        100,
        where=(ph_values <= 4.5),
        color="blue",
        alpha=0.2,
        label="Erosion Zone (Enhanced)",
    )

    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    return fig


def plot_ion_reservoir_simulation():
    """
    Visualization 2: Ion Reservoir Effect Simulation
    Demonstrates how the new material buffers acid attacks by releasing ions (Qsp > Ksp).
    """
    t = np.linspace(0, 20, 200)  # Time (minutes)
    acid_event = 5  # Acid attack at 5 min

    # 1. pH Profile
    ph_profile = np.ones_like(t) * 7.0
    # Sudden drop at t=5, then slow recovery
    ph_profile[t >= acid_event] = 7.0 - 3.0 * np.exp(
        -0.3 * (t[t >= acid_event] - acid_event)
    )

    # 2. Calcium Ion Availability (Local Micro-environment)
    # Normal Enamel: Structural loss, net loss of free ions due to wash-out/diffusion
    ca_normal = np.ones_like(t) * 1.0
    mask = t >= acid_event
    # Rapid drop representing demineralization and loss of structural integrity
    ca_normal[mask] = 1.0 - 0.6 * (1 - np.exp(-0.5 * (t[mask] - acid_event)))

    # New Material (PCFPC): Smart release
    # When pH drops, it releases ions to maintain local saturation
    ca_new = np.ones_like(t) * 1.0
    # Slight dip then boost (Reservoir effect)
    ca_new[mask] = (
        1.0
        - 0.1 * (1 - np.exp(-2 * (t[mask] - acid_event)))
        + 0.3 * (np.exp(-0.1 * (t[mask] - acid_event)) * np.sin(t[mask] - acid_event))
    )
    # Normalize to stabilize around 1.0 or higher (supersaturation maintenance)
    ca_new = np.clip(ca_new, 0, 1.2)

    # Create Subplots
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 8), sharex=True, gridspec_kw={"height_ratios": [1, 2]}
    )

    # Subplot 1: pH Change
    ax1.plot(t, ph_profile, color="purple", linestyle="-.", label="Oral pH Environment")
    ax1.axvline(x=acid_event, color="k", linestyle=":", alpha=0.5)
    ax1.set_ylabel("pH Level")
    ax1.set_title("Event: Acidic Solution Intake", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="lower right")

    # Subplot 2: Ion Availability
    ax2.plot(
        t,
        ca_normal,
        color="#ff4b4b",
        linewidth=2,
        label="Normal Enamel (Structural Loss)",
    )
    ax2.plot(
        t, ca_new, color="#2ca02c", linewidth=3, label="PCFPC (Ion Reservoir Release)"
    )

    # Annotations
    ax2.axhline(
        y=1.0, color="gray", linestyle="--", alpha=0.5, label="Equilibrium Baseline"
    )
    ax2.axvline(x=acid_event, color="k", linestyle=":", alpha=0.5)

    ax2.text(
        7, 0.6, "Demineralization\n(Qsp < Ksp)", color="#ff4b4b", fontweight="bold"
    )
    ax2.text(
        7,
        1.1,
        "Remineralization Support\n(Releasing Ca²⁺/PO₄³⁻)",
        color="#2ca02c",
        fontweight="bold",
    )

    ax2.set_ylabel("Undissolved Enamel Concentration (Relative Units)")
    ax2.set_xlabel("Time (minutes)")
    ax2.set_title("Mechanism: Smart Ion Release vs. Erosion", fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


class ToothAnimationGenerator:
    """
    Generates the tooth erosion and coating animation.
    """

    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-2, 4)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.title = self.ax.text(
            0, 3.8, "Initial State", ha="center", fontsize=15, fontweight="bold"
        )

        # Geometry
        self.x_tooth = np.linspace(-2.5, 2.5, 200)
        self.y_surface_base = (
            1.5 - 0.5 * np.cos(self.x_tooth * 2) - 0.2 * (self.x_tooth**2)
        )

        # Layers
        self.dentin_surface = self.y_surface_base - 0.8
        self._create_polygon(
            self.x_tooth, self.dentin_surface, -2, "moccasin", "Dentin"
        )

        self.current_enamel_y = self.y_surface_base.copy()
        self.enamel_poly = self.ax.fill_between(
            self.x_tooth,
            self.dentin_surface,
            self.current_enamel_y,
            color="whitesmoke",
            alpha=0.9,
            label="Enamel",
        )
        (self.enamel_line,) = self.ax.plot(
            self.x_tooth, self.current_enamel_y, color="gray", lw=1
        )

        # Particles
        (self.acid_particles,) = self.ax.plot(
            [], [], "ro", markersize=4, alpha=0.6, label="Acid (H+)"
        )
        self.acid_x = np.random.uniform(-2.5, 2.5, 100)
        self.acid_y = np.random.uniform(2.0, 3.5, 100)

        # Second acid attack particles for phase 4
        (self.acid_particles2,) = self.ax.plot(
            [], [], "ro", markersize=4, alpha=0.6, label="Second Acid Attack"
        )
        self.acid_x2 = np.random.uniform(-2.5, 2.5, 80)
        self.acid_y2 = np.random.uniform(2.0, 3.5, 80)

        # Ion reservoir particles (Ca2+, PO4-) from coating
        (self.ion_particles,) = self.ax.plot(
            [], [], "bo", markersize=3, alpha=0.7, label="Released Ions (Ca²⁺/PO₄³⁻)"
        )
        self.ion_x = []
        self.ion_y = []

        self.coating_poly = None
        self.coating_thickness = 0

    def _create_polygon(self, x, y_top, y_bottom, color, label):
        verts = [(x[0], y_bottom), *zip(x, y_top), (x[-1], y_bottom)]
        poly = Polygon(verts, facecolor=color, edgecolor="none", label=label)
        self.ax.add_patch(poly)

    def update(self, frame):
        if frame < 60:  # Acid Attack
            self.title.set_text("Phase 1: Acid Attack (pH < 5.5)")
            self.acid_y -= 0.05
            mask = self.acid_y < np.interp(
                self.acid_x, self.x_tooth, self.current_enamel_y
            )
            self.acid_y[mask] = (
                np.interp(self.acid_x[mask], self.x_tooth, self.current_enamel_y) + 0.1
            )
            self.acid_particles.set_data(self.acid_x, self.acid_y)

        elif frame < 120:  # Erosion
            self.title.set_text("Phase 2: Enamel Erosion")
            self.title.set_color("red")
            erosion = 0.015 * np.sin(frame) + 0.008 * np.random.rand(len(self.x_tooth))
            self.current_enamel_y = np.maximum(
                self.current_enamel_y - erosion, self.dentin_surface + 0.05
            )

            self.enamel_poly.remove()
            self.enamel_poly = self.ax.fill_between(
                self.x_tooth,
                self.dentin_surface,
                self.current_enamel_y,
                color="#E8E8E8",
                alpha=0.9,
            )
            self.enamel_line.set_ydata(self.current_enamel_y)
            if frame % 2 == 0:
                self.acid_particles.set_alpha(max(0, 0.6 - (frame - 60) / 100))

        elif frame < 180:  # Coating Application
            self.title.set_text("Phase 3: PCFPC Coating Application")
            self.title.set_color("blue")
            self.acid_particles.set_visible(False)

            self.coating_thickness = (frame - 120) * 0.005
            target = np.minimum(
                self.current_enamel_y + self.coating_thickness,
                self.current_enamel_y + 0.3,
            )
            if self.coating_poly:
                self.coating_poly.remove()
            self.coating_poly = self.ax.fill_between(
                self.x_tooth, self.current_enamel_y, target, color="skyblue", alpha=0.6
            )

        else:  # Phase 4: Acid Resistance Test with Ion Reservoir Effect
            self.title.set_text(
                "Phase 4: Ion Reservoir Protection - Ca²⁺/PO₄³⁻ Release"
            )
            self.title.set_color("green")

            # Second acid attack
            self.acid_y2 -= 0.06
            coating_surface = np.interp(
                self.acid_x2,
                self.x_tooth,
                self.current_enamel_y + self.coating_thickness,
            )
            mask2 = self.acid_y2 < coating_surface

            # When acid hits coating, generate ions from coating surface
            for i in np.where(mask2)[0][:3]:  # Limit ion generation rate
                if len(self.ion_x) < 50:  # Maximum ions
                    # Generate ions from coating surface where acid hits
                    ion_start_x = self.acid_x2[i] + np.random.uniform(-0.1, 0.1)
                    ion_start_y = coating_surface[i] + 0.05
                    self.ion_x.append(ion_start_x)
                    self.ion_y.append(ion_start_y)

            # Move ions upward (released from coating)
            for j in range(len(self.ion_x)):
                self.ion_y[j] += 0.03  # Ion release velocity
                self.ion_x[j] += np.random.uniform(-0.01, 0.01)  # Random drift

            # Remove ions that go too high
            self.ion_x = [x for x, y in zip(self.ion_x, self.ion_y) if y < 3.0]
            self.ion_y = [y for y in self.ion_y if y < 3.0]

            # Acid hits coating but bounces off (no penetration due to ion reservoir)
            self.acid_y2[mask2] = coating_surface[mask2] + 0.15

            self.acid_particles2.set_data(self.acid_x2, self.acid_y2)
            self.ion_particles.set_data(self.ion_x, self.ion_y)

            # Add ion reservoir explanation text
            if frame == 200:
                self.ax.text(
                    0,
                    2.0,
                    "Ion Reservoir Effect:\nCa²⁺/PO₄³⁻ ions maintain Qsp > Ksp",
                    ha="center",
                    color="blue",
                    fontsize=10,
                    fontweight="bold",
                    bbox=dict(
                        boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8
                    ),
                )

        return (
            self.enamel_line,
            self.acid_particles,
            self.acid_particles2,
            self.ion_particles,
        )

    def create_gif(self):
        ani = animation.FuncAnimation(self.fig, self.update, frames=250, interval=50)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as tmp:
            try:
                ani.save(tmp.name, writer="pillow", fps=15)
                return tmp.name
            except Exception as e:
                return None


def main():
    st.title("AP Chemistry")
    st.title("치아 법랑질 부식의 원인; 산-염기 반응을 중심으로")
    st.markdown("---")

    # 탭 레이아웃
    tab1, tab2, tab3 = st.tabs(["1. 원인 (pH)", "2. 메커니즘 (이온)", "3. 시각화"])

    with tab1:
        st.header("용해도 vs. pH")
        st.pyplot(plot_ph_solubility())
        st.info(
            "**핵심:** pH 임계값을 5.5에서 4.5로 낮춰서, 산성 구강 환경에서 안정성 범위를 크게 확장합니다."
        )

    with tab2:
        st.header("메커니즘")
        st.pyplot(plot_ion_reservoir_simulation())
        st.success(
            "**메커니즘:** 구조적 이온을 잃는 일반 법랑질($Q_{sp} < K_{sp}$)과 달리, PCFPC 물질은 저장소 역할을 하여 산 공격 중 포화도를 유지하기 위해 이온을 방출합니다($Q_{sp} < K_{sp}$)."
        )

    with tab3:
        st.header("시각화")
        if st.button("▶️ 애니메이션 생성 (약 10초)"):
            with st.spinner("화학 반응 시각화 중..."):
                gen = ToothAnimationGenerator()
                gif_path = gen.create_gif()
                if gif_path:
                    st.image(gif_path, caption="산 공격 -> 부식 -> PCFPC 복구 과정")
                    os.unlink(gif_path)
                else:
                    st.error(
                        "애니메이션을 생성할 수 없습니다. 'pillow'가 설치되어 있는지 확인해주세요."
                    )

    st.markdown("---")
    st.caption("AP Chemistry 프로젝트 | Python & Streamlit으로 구동되는 시각화")


if __name__ == "__main__":
    main()
