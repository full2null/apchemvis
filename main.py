import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
import numpy as np

# 한글 폰트 설정 (패키지가 없으면 영문으로 표시됨)
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


def plot_ph_solubility():
    """법랑질 부식 원인 분석: pH와 용해도의 관계"""

    # pH 값 범위 설정 (산성~중성~염기성)
    ph_values = np.linspace(3, 8, 100)

    # 하이드록시아파타이트(일반 법랑질)의 용해도 모델링
    # pH가 낮을수록(산성) 용해도가 급격히 증가
    solubility_hap = 10 ** (5.5 - ph_values)

    # 불소화된 아파타이트는 더 강한 내산성 (임계 pH 4.5)
    solubility_fap = 10 ** (4.5 - ph_values)

    # 그래프 생성
    plt.figure(figsize=(10, 6))
    plt.plot(
        ph_values,
        solubility_hap,
        label="일반 법랑질 (Hydroxyapatite)",
        color="red",
        linewidth=2.5,
    )
    plt.plot(
        ph_values,
        solubility_fap,
        label="불소 도포됨 (Fluorapatite)",
        color="blue",
        linestyle="--",
        linewidth=2,
    )

    # 임계 pH 표시
    plt.axvline(
        x=5.5, color="gray", linestyle=":", alpha=0.7, label="Critical pH (5.5)"
    )
    plt.text(
        5.6,
        80,
        "탈회 시작점\n(pH 5.5)",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
    )

    # 그래프 설정
    plt.title(
        "치아 법랑질 부식 원인: pH 변화에 따른 용해도", fontsize=14, fontweight="bold"
    )
    plt.xlabel("pH (산성 ← → 염기성)")
    plt.ylabel("상대적 용해도 (Relative Solubility)")
    plt.xlim(8, 3)  # x축 반전 (오른쪽이 염기성)
    plt.ylim(0, 100)
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 그래프 저장 및 표시
    plt.tight_layout()
    plt.savefig("ph_solubility_analysis.png", dpi=300, bbox_inches="tight")
    print("그래프가 'ph_solubility_analysis.png'로 저장되었습니다.")
    plt.show()


class ToothSimulation:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-2, 4)
        self.ax.set_aspect("equal")
        self.ax.axis("off")  # 축 숨기기

        # 타이틀
        self.title = self.ax.text(
            0,
            3.8,
            "초기 상태: 건강한 치아 (Enamel)",
            ha="center",
            fontsize=15,
            fontweight="bold",
        )

        # 치아 형상 데이터 생성 (Molar - 어금니 단면 모양)
        self.x_tooth = np.linspace(-2.5, 2.5, 200)
        # 어금니 윗부분(Crown)의 굴곡을 수학적으로 근사
        self.y_surface_base = (
            1.5 - 0.5 * np.cos(self.x_tooth * 2) - 0.2 * (self.x_tooth**2)
        )
        self.y_root = -2 * np.ones_like(self.x_tooth)  # 뿌리 쪽

        # 1. 상아질 (Dentin) - 안쪽 층 (노란색)
        self.dentin_surface = self.y_surface_base - 0.8
        self.dentin_poly = self._create_polygon(
            self.x_tooth, self.dentin_surface, -2, "moccasin", "Dentin (상아질)"
        )

        # 2. 법랑질 (Enamel) - 바깥쪽 층 (흰색/회색)
        self.current_enamel_y = self.y_surface_base.copy()
        self.enamel_poly = self.ax.fill_between(
            self.x_tooth,
            self.dentin_surface,
            self.current_enamel_y,
            color="whitesmoke",
            alpha=0.9,
            label="Enamel (법랑질)",
        )

        # 외곽선 그리기
        (self.enamel_line,) = self.ax.plot(
            self.x_tooth, self.current_enamel_y, color="gray", lw=1
        )

        # 3. 산성 입자 (Acid H+) - 초기엔 안 보임
        (self.acid_particles,) = self.ax.plot(
            [], [], "ro", markersize=4, alpha=0.6, label="Acid ($H^+$)"
        )
        self.acid_x = np.random.uniform(-2.5, 2.5, 100)
        self.acid_y = np.random.uniform(2.0, 3.5, 100)

        # 4. 코팅 층 (Coating) - 초기엔 안 보임
        self.coating_poly = None

    def _create_polygon(self, x, y_top, y_bottom, color, label):
        verts = [(x[0], y_bottom), *zip(x, y_top), (x[-1], y_bottom)]
        poly = Polygon(verts, facecolor=color, edgecolor="none", label=label)
        self.ax.add_patch(poly)
        return poly

    def update(self, frame):
        # Phase 1: Acid Attack (Frame 0-60)
        if frame < 60:
            self.title.set_text(f"단계 1: 산성 물질 공격 (pH < 5.5) - 시간: {frame}")
            # 산성 입자가 아래로 떨어짐
            drop_speed = 0.05
            self.acid_y -= drop_speed

            # 치아 표면에 닿으면 멈춤
            mask = self.acid_y < np.interp(
                self.acid_x, self.x_tooth, self.current_enamel_y
            )
            self.acid_y[mask] = (
                np.interp(self.acid_x[mask], self.x_tooth, self.current_enamel_y) + 0.1
            )

            self.acid_particles.set_data(self.acid_x, self.acid_y)

        # Phase 2: Erosion (Frame 60-120)
        elif frame < 120:
            self.title.set_text("단계 2: 법랑질 부식 (Ca10(PO4)6(OH)2 용해)")
            self.title.set_color("red")

            # 표면이 불규칙하게 깎여나감 (Random noise 추가)
            erosion_factor = 0.005 * np.sin(frame) + 0.002 * np.random.rand(
                len(self.x_tooth)
            )
            self.current_enamel_y -= erosion_factor

            # 너무 많이 깎이지 않게 상아질보다는 위에 있도록 제한
            self.current_enamel_y = np.maximum(
                self.current_enamel_y, self.dentin_surface + 0.1
            )

            # 그래프 업데이트 (fill_between은 update가 까다로워 지우고 다시 그림)
            self.enamel_poly.remove()
            self.enamel_poly = self.ax.fill_between(
                self.x_tooth,
                self.dentin_surface,
                self.current_enamel_y,
                color="#E8E8E8",
                alpha=0.9,
            )
            self.enamel_line.set_ydata(self.current_enamel_y)

            # 산성 입자 서서히 사라짐
            if frame % 2 == 0:
                self.acid_particles.set_alpha(max(0, 0.6 - (frame - 60) / 100))

        # Phase 3: Protection/Coating (Frame 120-200)
        else:
            self.title.set_text("단계 3: 새로운 코팅 물질 적용 (재광화/보호)")
            self.title.set_color("blue")
            self.acid_particles.set_visible(False)

            # 코팅층 형성 (원래 표면보다 살짝 위로 매끄럽게)
            coating_thickness = (frame - 120) * 0.005
            target_coating = self.current_enamel_y + coating_thickness

            # 최대 두께 제한
            target_coating = np.minimum(target_coating, self.current_enamel_y + 0.3)

            if self.coating_poly:
                self.coating_poly.remove()

            self.coating_poly = self.ax.fill_between(
                self.x_tooth,
                self.current_enamel_y,
                target_coating,
                color="skyblue",
                alpha=0.6,
                label="New Coating",
            )

            # 텍스트 추가
            if frame == 150:
                self.ax.text(
                    0,
                    2.5,
                    "불소/CPP-ACP 보호막 형성",
                    ha="center",
                    color="blue",
                    fontsize=12,
                )

        return self.enamel_line, self.acid_particles

    def start(self):
        ani = animation.FuncAnimation(
            self.fig, self.update, frames=200, interval=50, repeat=False
        )
        plt.legend(loc="lower right")
        plt.show()


def run_tooth_animation():
    """치아 부식 및 복구 애니메이션 실행"""
    print("치아 부식 및 복구 시뮬레이션 애니메이션을 시작합니다...")
    sim = ToothSimulation()
    sim.start()


def main():
    print("AP Chemistry 치아 법랑질 부식 시각화 프로그램")
    print("=" * 50)

    print("\n모든 시각화를 자동으로 실행합니다...")

    # 1. pH와 용해도 관계 그래프
    print("\n1. 법랑질 부식 원인 분석 그래프 생성 중...")
    plot_ph_solubility()

    # 사용자가 그래프를 확인할 시간 제공
    input("\n첫 번째 그래프를 확인한 후 Enter를 누르면 애니메이션이 시작됩니다...")

    # 2. 치아 부식 및 복구 애니메이션
    print("\n2. 치아 부식 및 복구 애니메이션 시작...")
    run_tooth_animation()

    print("\n모든 시각화가 완료되었습니다!")


if __name__ == "__main__":
    main()
