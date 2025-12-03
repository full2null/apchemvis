import os
import tempfile

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.patches import Polygon

# English font settings for AP Chemistry presentation
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

# Streamlit page configuration
st.set_page_config(
    page_title="AP Chemistry: Tooth Enamel Erosion Visualization",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)


def plot_ph_solubility():
    """Enamel erosion analysis: pH vs solubility relationship"""

    # pH value range (acidic to neutral to basic)
    ph_values = np.linspace(3, 8, 100)

    # Hydroxyapatite (normal enamel) solubility modeling
    # Lower pH (acidic) causes exponential increase in solubility
    solubility_hap = 10 ** (5.5 - ph_values)

    # Fluorinated apatite has stronger acid resistance (critical pH 4.5)
    solubility_fap = 10 ** (4.5 - ph_values)

    # Create graph
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        ph_values,
        solubility_hap,
        label="Normal Enamel (Hydroxyapatite)",
        color="red",
        linewidth=2.5,
    )
    ax.plot(
        ph_values,
        solubility_fap,
        label="Fluoride-treated (Fluorapatite)",
        color="blue",
        linestyle="--",
        linewidth=2,
    )

    # Critical pH indicator
    ax.axvline(x=5.5, color="gray", linestyle=":", alpha=0.7, label="Critical pH (5.5)")
    ax.text(
        5.6,
        80,
        "Demineralization\nStarts (pH 5.5)",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
    )

    # Graph settings
    ax.set_title(
        "Tooth Enamel Erosion: Solubility vs pH Changes", fontsize=14, fontweight="bold"
    )
    ax.set_xlabel("pH (Acidic ← → Basic)")
    ax.set_ylabel("Relative Solubility")
    ax.set_xlim(8, 3)  # Reverse x-axis (right side is basic)
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


def plot_coating_comparison():
    """Coating material effectiveness comparison"""

    materials = [
        "Normal Enamel",
        "Resin Coating",
        "Glass Particle",
        "CPP-ACP",
        "Fluoride Treatment",
    ]

    # Effectiveness indicators for each coating (based on research data)
    acid_resistance = [20, 65, 70, 80, 85]  # Acid resistance (%)
    durability = [30, 75, 80, 70, 90]  # Durability (%)
    remineralization = [10, 40, 45, 90, 75]  # Remineralization capability (%)

    x = np.arange(len(materials))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 7))

    bars1 = ax.bar(
        x - width,
        acid_resistance,
        width,
        label="Acid Resistance",
        color="#ff7f7f",
        alpha=0.8,
    )
    bars2 = ax.bar(x, durability, width, label="Durability", color="#7fbfff", alpha=0.8)
    bars3 = ax.bar(
        x + width,
        remineralization,
        width,
        label="Remineralization",
        color="#7fff7f",
        alpha=0.8,
    )

    ax.set_xlabel("Coating Material Type")
    ax.set_ylabel("Effectiveness Index (%)")
    ax.set_title(
        "Coating Material Protection Effectiveness Comparison",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(materials, rotation=15, ha="right")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    # Display values
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                f"{height}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    plt.tight_layout()
    return fig


def plot_chemical_compatibility():
    """Chemical compatibility of new coating materials"""

    properties = [
        "Biocompatibility",
        "Adhesion",
        "Wear Resistance",
        "Transparency",
        "Cost-Effectiveness",
    ]

    # Scores for each material (1-10 scale)
    resin = [8, 9, 7, 6, 7]
    glass_particle = [7, 8, 9, 8, 6]
    cpp_acp = [9, 6, 6, 9, 5]
    fluoride = [9, 7, 8, 10, 9]
    new_coating = [9, 8, 8, 8, 8]  # Proposed new coating

    # Generate radar chart
    angles = np.linspace(0, 2 * np.pi, len(properties), endpoint=False).tolist()
    angles += angles[:1]  # For closed polygon

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection="polar"))

    # Plot data for each material
    materials_data = [
        (resin + resin[:1], "Resin", "#ff6b6b"),
        (glass_particle + glass_particle[:1], "Glass Particle", "#4ecdc4"),
        (cpp_acp + cpp_acp[:1], "CPP-ACP", "#45b7d1"),
        (fluoride + fluoride[:1], "Fluoride", "#f9ca24"),
        (new_coating + new_coating[:1], "New Coating", "#6c5ce7"),
    ]

    for data, label, color in materials_data:
        ax.plot(angles, data, "o-", linewidth=2, label=label, color=color)
        ax.fill(angles, data, alpha=0.15, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(properties)
    ax.set_ylim(0, 10)
    ax.set_title(
        "Chemical Compatibility Comparison by Coating Material",
        size=14,
        fontweight="bold",
        pad=20,
    )
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))
    ax.grid(True)

    return fig


class ToothAnimationGenerator:
    """Real animation generator for tooth erosion and recovery process"""

    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-2, 4)
        self.ax.set_aspect("equal")
        self.ax.axis("off")

        # Title
        self.title = self.ax.text(
            0,
            3.8,
            "Initial State: Healthy Tooth Enamel",
            ha="center",
            fontsize=15,
            fontweight="bold",
        )

        # Tooth geometry data (Molar cross-section)
        self.x_tooth = np.linspace(-2.5, 2.5, 200)
        self.y_surface_base = (
            1.5 - 0.5 * np.cos(self.x_tooth * 2) - 0.2 * (self.x_tooth**2)
        )

        # 1. Dentin (inner layer)
        self.dentin_surface = self.y_surface_base - 0.8
        self.dentin_poly = self._create_polygon(
            self.x_tooth, self.dentin_surface, -2, "moccasin", "Dentin"
        )

        # 2. Enamel (outer layer)
        self.current_enamel_y = self.y_surface_base.copy()
        self.enamel_poly = self.ax.fill_between(
            self.x_tooth,
            self.dentin_surface,
            self.current_enamel_y,
            color="whitesmoke",
            alpha=0.9,
            label="Enamel",
        )

        # Outline
        (self.enamel_line,) = self.ax.plot(
            self.x_tooth, self.current_enamel_y, color="gray", lw=1
        )

        # 3. Acid particles (H+) - initially hidden
        (self.acid_particles,) = self.ax.plot(
            [], [], "ro", markersize=4, alpha=0.6, label="Acid (H+)"
        )
        self.acid_x = np.random.uniform(-2.5, 2.5, 100)
        self.acid_y = np.random.uniform(2.0, 3.5, 100)

        # 4. Coating layer - initially hidden
        self.coating_poly = None

    def _create_polygon(self, x, y_top, y_bottom, color, label):
        verts = [(x[0], y_bottom), *zip(x, y_top), (x[-1], y_bottom)]
        poly = Polygon(verts, facecolor=color, edgecolor="none", label=label)
        self.ax.add_patch(poly)
        return poly

    def update(self, frame):
        # Phase 1: Acid Attack (Frame 0-60)
        if frame < 60:
            self.title.set_text(f"Phase 1: Acid Attack (pH < 5.5) - Frame: {frame}")
            self.title.set_color("black")

            # Acid particles falling down
            drop_speed = 0.05
            self.acid_y -= drop_speed

            # Stop when touching tooth surface
            mask = self.acid_y < np.interp(
                self.acid_x, self.x_tooth, self.current_enamel_y
            )
            self.acid_y[mask] = (
                np.interp(self.acid_x[mask], self.x_tooth, self.current_enamel_y) + 0.1
            )

            self.acid_particles.set_data(self.acid_x, self.acid_y)

        # Phase 2: Erosion (Frame 60-120)
        elif frame < 120:
            self.title.set_text("Phase 2: Enamel Erosion (Ca10(PO4)6(OH)2 Dissolution)")
            self.title.set_color("red")

            # Surface irregularly eroded
            erosion_factor = 0.005 * np.sin(frame) + 0.002 * np.random.rand(
                len(self.x_tooth)
            )
            self.current_enamel_y -= erosion_factor

            # Limit erosion to stay above dentin
            self.current_enamel_y = np.maximum(
                self.current_enamel_y, self.dentin_surface + 0.1
            )

            # Update graph
            self.enamel_poly.remove()
            self.enamel_poly = self.ax.fill_between(
                self.x_tooth,
                self.dentin_surface,
                self.current_enamel_y,
                color="#E8E8E8",
                alpha=0.9,
            )
            self.enamel_line.set_ydata(self.current_enamel_y)

            # Acid particles gradually disappear
            if frame % 2 == 0:
                self.acid_particles.set_alpha(max(0, 0.6 - (frame - 60) / 100))

        # Phase 3: Protection/Coating (Frame 120-200)
        else:
            self.title.set_text(
                "Phase 3: New Coating Application (Remineralization/Protection)"
            )
            self.title.set_color("blue")
            self.acid_particles.set_visible(False)

            # Coating layer formation
            coating_thickness = (frame - 120) * 0.005
            target_coating = self.current_enamel_y + coating_thickness

            # Maximum thickness limit
            target_coating = np.minimum(target_coating, self.current_enamel_y + 0.3)

            if self.coating_poly:
                self.coating_poly.remove()

            self.coating_poly = self.ax.fill_between(
                self.x_tooth,
                self.current_enamel_y,
                target_coating,
                color="skyblue",
                alpha=0.6,
                label="Protective Coating",
            )

            # Add text
            if frame == 150:
                self.ax.text(
                    0,
                    2.5,
                    "Fluoride/CPP-ACP Protective Layer Formation",
                    ha="center",
                    color="blue",
                    fontsize=12,
                )

        return self.enamel_line, self.acid_particles

    def create_animation(self):
        """Create and save animation as GIF"""
        ani = animation.FuncAnimation(
            self.fig, self.update, frames=200, interval=50, repeat=False
        )
        plt.legend(loc="lower right")

        # Try different writers for compatibility
        writers_to_try = ["pillow", "imagemagick", "ffmpeg"]

        for writer in writers_to_try:
            try:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".gif"
                ) as tmp_file:
                    ani.save(tmp_file.name, writer=writer, fps=10)
                    return tmp_file.name, "gif"
            except Exception as _:
                continue

        # If all writers fail, return None to fallback to static images
        raise Exception(
            "No suitable animation writer found. Please install pillow: pip install pillow"
        )


class ToothSimulationStatic:
    """Static image visualization of tooth erosion process"""

    def create_stages(self):
        """Generate 3-stage tooth erosion process as static images"""

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        for i, (ax, title, color) in enumerate(
            zip(
                axes,
                [
                    "Stage 1: Acid Attack",
                    "Stage 2: Enamel Erosion",
                    "Stage 3: Coating Protection",
                ],
                ["red", "orange", "blue"],
            )
        ):
            # Tooth geometry data generation
            x_tooth = np.linspace(-2.5, 2.5, 200)
            y_surface_base = 1.5 - 0.5 * np.cos(x_tooth * 2) - 0.2 * (x_tooth**2)

            # Dentin (inner layer)
            dentin_surface = y_surface_base - 0.8
            ax.fill_between(
                x_tooth, -2, dentin_surface, color="moccasin", alpha=0.9, label="Dentin"
            )

            if i == 0:  # Stage 1: Healthy tooth + acid particles
                enamel_y = y_surface_base
                ax.fill_between(
                    x_tooth,
                    dentin_surface,
                    enamel_y,
                    color="whitesmoke",
                    alpha=0.9,
                    label="Enamel",
                )
                # Acid particle display
                acid_x = np.random.uniform(-2.5, 2.5, 50)
                acid_y = np.random.uniform(2.0, 3.0, 50)
                ax.scatter(acid_x, acid_y, c="red", s=20, alpha=0.7, label="Acid (H+)")

            elif i == 1:  # Stage 2: Eroded tooth
                # Irregularly eroded surface
                erosion = 0.1 * np.random.rand(len(x_tooth))
                enamel_y = y_surface_base - erosion
                ax.fill_between(
                    x_tooth,
                    dentin_surface,
                    enamel_y,
                    color="#E8E8E8",
                    alpha=0.9,
                    label="Eroded Enamel",
                )

            else:  # Stage 3: Coated tooth
                erosion = 0.1 * np.random.rand(len(x_tooth))
                enamel_y = y_surface_base - erosion
                ax.fill_between(
                    x_tooth, dentin_surface, enamel_y, color="#E8E8E8", alpha=0.9
                )
                # Add coating layer
                coating_y = enamel_y + 0.2
                ax.fill_between(
                    x_tooth,
                    enamel_y,
                    coating_y,
                    color="skyblue",
                    alpha=0.6,
                    label="Protective Coating",
                )

            ax.plot(
                x_tooth,
                y_surface_base if i == 0 else enamel_y,
                color="gray",
                linewidth=1,
            )
            ax.set_xlim(-3, 3)
            ax.set_ylim(-2, 4)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.set_title(title, fontsize=12, fontweight="bold", color=color)
            ax.legend(loc="lower right", fontsize=8)

        plt.tight_layout()
        return fig


def main():
    # Main title
    st.title("🦷 AP Chemistry: Tooth Enamel Erosion and Protection Visualization")
    st.markdown("---")

    # Sidebar menu
    st.sidebar.title("📊 Visualization Menu")

    # Animation toggle
    show_animation = st.sidebar.checkbox("Show Real Animation (GIF)", value=False)
    st.sidebar.markdown("*Note: Animation generation may take 10-20 seconds*")
    st.sidebar.markdown("*Requires: pillow package for animation support*")

    # Display all visualizations
    st.header("1. Enamel Erosion Analysis")
    st.subheader("Solubility vs pH Changes")

    fig1 = plot_ph_solubility()
    st.pyplot(fig1)

    st.markdown("""
    **Analysis Results:**
    - Normal enamel (hydroxyapatite) begins demineralization at pH 5.5
    - Fluoride-treated enamel (fluorapatite) resists down to pH 4.5
    - Acidic beverages (pH 2-4) cause rapid dissolution
    """)

    st.markdown("---")

    # Coating effectiveness comparison
    st.header("2. Coating Material Protection Effectiveness")

    fig2 = plot_coating_comparison()
    st.pyplot(fig2)

    st.markdown("""
    **Effectiveness Analysis:**
    - **CPP-ACP**: Highest remineralization capability (90%)
    - **Fluoride Treatment**: Well-balanced overall protection
    - **Glass Particle Coating**: Excellent durability (80%)
    - **Resin Coating**: Superior adhesion but limited remineralization
    """)

    st.markdown("---")

    # Tooth erosion process visualization
    st.header("3. Tooth Erosion and Recovery Process")

    if show_animation:
        st.subheader("🎬 Real-time Animation")
        with st.spinner("Generating animation... Please wait 10-20 seconds"):
            try:
                anim_gen = ToothAnimationGenerator()
                anim_path, file_type = anim_gen.create_animation()

                # Display animation (GIF)
                if file_type == "gif":
                    # For GIF, use st.image with animation
                    st.image(anim_path, caption="Tooth Erosion and Recovery Process")
                else:
                    # For video files, use st.video
                    with open(anim_path, "rb") as video_file:
                        video_bytes = video_file.read()
                        st.video(video_bytes)

                # Cleanup
                os.unlink(anim_path)

            except Exception as e:
                st.error(f"Animation generation failed: {str(e)}")
                st.info("Showing static images instead...")
                st.markdown(
                    "**Tip:** Install pillow for animation support: `pip install pillow`"
                )
                tooth_sim = ToothSimulationStatic()
                fig3 = tooth_sim.create_stages()
                st.pyplot(fig3)
    else:
        st.subheader("📊 Static Process Images")
        tooth_sim = ToothSimulationStatic()
        fig3 = tooth_sim.create_stages()
        st.pyplot(fig3)

    st.markdown("""
    **Erosion and Recovery Mechanism:**
    1. **Acid Attack**: H⁺ ions attack enamel surface
    2. **Enamel Erosion**: Ca₁₀(PO₄)₆(OH)₂ structure dissolution
    3. **Coating Protection**: New protective layer for remineralization and protection
    """)

    st.markdown("---")

    # Chemical compatibility analysis
    st.header("4. Chemical Compatibility of New Coating Materials")

    fig4 = plot_chemical_compatibility()
    st.pyplot(fig4)

    st.markdown("""
    **Compatibility Assessment:**
    - **New Coating Material** shows balanced performance across all metrics (average 8.2/10)
    - Proposes composite coating strategy combining advantages of existing materials
    - Solution that satisfies both biocompatibility and economic feasibility
    """)

    st.markdown("---")

    # Conclusions and recommendations
    st.header("5. Conclusions and Recommendations")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔬 Chemical Mechanism Summary")
        st.markdown("""
        1. **Erosion Principle**: Hydroxyapatite dissolution in acidic environment
        2. **Protection Strategy**: Multi-layer coating system application
        3. **Remineralization**: Synergistic effect of CPP-ACP and fluoride
        """)

    with col2:
        st.subheader("💡 New Coating Material Proposal")
        st.markdown("""
        - **Base Layer**: Fluoride-based remineralization layer
        - **Middle Layer**: CPP-ACP buffer layer  
        - **Surface Layer**: Glass particle-reinforced resin
        """)

    # Additional information
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Developer Information**
    
    🎓 AP Chemistry Presentation Visualization Tool
    
    📊 Python + Streamlit Based
    
    🔬 Scientific Data-driven Simulation
    """)


if __name__ == "__main__":
    main()
