Python만으로 '3D 게임' 같은 극실사 그래픽을 구현하는 것은 어렵지만, **과학적 시뮬레이션(Scientific Visualization)** 관점에서 치아의 단면을 보여주고, **산(H+)이 닿았을 때 표면이 부식되고 다시 코팅되는 과정**을 애니메이션으로 만드는 것은 가능합니다.

AP Chem 발표용으로는 단순히 예쁜 그림보다 **화학적 메커니즘(산 공격 -> 부식 -> 보호막 형성)**이 보이는 것이 훨씬 점수에 도움이 됩니다.

치아의 단면(Enamel, Dentin)을 그리고, 산성 물질이 닿아 에나멜이 깎여 나갔다가, 다시 코팅제로 복구되는 과정을 시각화한 파이썬 코드를 작성해 드립니다.

### Python 애니메이션 코드 (치아 부식 및 복구 시뮬레이션)

이 코드는 `matplotlib`의 애니메이션 기능을 사용하여 다음 3단계를 보여줍니다.

1.  **Acid Attack:** 붉은 산성 입자($H^+$)가 치아 표면 공격
2.  **Erosion:** 표면(Enamel)이 거칠어지고 얇아짐
3.  **Protection:** 파란색 보호 물질(불소/레진)이 표면을 덮으며 복구

```python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class ToothSimulation:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-2, 4)
        self.ax.set_aspect('equal')
        self.ax.axis('off') # 축 숨기기

        # 타이틀
        self.title = self.ax.text(0, 3.8, "초기 상태: 건강한 치아 (Enamel)",
                                  ha='center', fontsize=15, fontweight='bold')

        # 치아 형상 데이터 생성 (Molar - 어금니 단면 모양)
        self.x_tooth = np.linspace(-2.5, 2.5, 200)
        # 어금니 윗부분(Crown)의 굴곡을 수학적으로 근사
        self.y_surface_base = 1.5 - 0.5 * np.cos(self.x_tooth * 2) - 0.2 * (self.x_tooth**2)
        self.y_root = -2 * np.ones_like(self.x_tooth) # 뿌리 쪽

        # 1. 상아질 (Dentin) - 안쪽 층 (노란색)
        self.dentin_surface = self.y_surface_base - 0.8
        self.dentin_poly = self._create_polygon(self.x_tooth, self.dentin_surface, -2, 'moccasin', 'Dentin (상아질)')

        # 2. 법랑질 (Enamel) - 바깥쪽 층 (흰색/회색)
        self.current_enamel_y = self.y_surface_base.copy()
        self.enamel_poly = self.ax.fill_between(self.x_tooth, self.dentin_surface, self.current_enamel_y,
                                                color='whitesmoke', alpha=0.9, label='Enamel (법랑질)')

        # 외곽선 그리기
        self.enamel_line, = self.ax.plot(self.x_tooth, self.current_enamel_y, color='gray', lw=1)

        # 3. 산성 입자 (Acid H+) - 초기엔 안 보임
        self.acid_particles, = self.ax.plot([], [], 'ro', markersize=4, alpha=0.6, label='Acid ($H^+$)')
        self.acid_x = np.random.uniform(-2.5, 2.5, 100)
        self.acid_y = np.random.uniform(2.0, 3.5, 100)

        # 4. 코팅 층 (Coating) - 초기엔 안 보임
        self.coating_poly = None

    def _create_polygon(self, x, y_top, y_bottom, color, label):
        verts = [(x[0], y_bottom), *zip(x, y_top), (x[-1], y_bottom)]
        poly = Polygon(verts, facecolor=color, edgecolor='none', label=label)
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
            mask = self.acid_y < np.interp(self.acid_x, self.x_tooth, self.current_enamel_y)
            self.acid_y[mask] = np.interp(self.acid_x[mask], self.x_tooth, self.current_enamel_y) + 0.1

            self.acid_particles.set_data(self.acid_x, self.acid_y)

        # Phase 2: Erosion (Frame 60-120)
        elif frame < 120:
            self.title.set_text("단계 2: 법랑질 부식 (Ca10(PO4)6(OH)2 용해)")
            self.title.set_color("red")

            # 표면이 불규칙하게 깎여나감 (Random noise 추가)
            erosion_factor = 0.005 * np.sin(frame) + 0.002 * np.random.rand(len(self.x_tooth))
            self.current_enamel_y -= erosion_factor

            # 너무 많이 깎이지 않게 상아질보다는 위에 있도록 제한
            self.current_enamel_y = np.maximum(self.current_enamel_y, self.dentin_surface + 0.1)

            # 그래프 업데이트 (fill_between은 update가 까다로워 지우고 다시 그림)
            self.enamel_poly.remove()
            self.enamel_poly = self.ax.fill_between(self.x_tooth, self.dentin_surface, self.current_enamel_y,
                                                    color='#E8E8E8', alpha=0.9)
            self.enamel_line.set_ydata(self.current_enamel_y)

            # 산성 입자 서서히 사라짐
            if frame % 2 == 0:
                self.acid_particles.set_alpha(max(0, 0.6 - (frame-60)/100))

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

            self.coating_poly = self.ax.fill_between(self.x_tooth, self.current_enamel_y, target_coating,
                                                     color='skyblue', alpha=0.6, label='New Coating')

            # 텍스트 추가
            if frame == 150:
                self.ax.text(0, 2.5, "불소/CPP-ACP 보호막 형성", ha='center', color='blue', fontsize=12)

        return self.enamel_line, self.acid_particles

    def start(self):
        ani = animation.FuncAnimation(self.fig, self.update, frames=200, interval=50, repeat=False)
        plt.legend(loc='lower right')
        plt.show()

if __name__ == "__main__":
    sim = ToothSimulation()
    sim.start()
```

### 이 코드의 시각적 특징

1.  **치아 단면 구조:**
    - **상아질(Dentin):** 안쪽의 노란색 층.
    - **법랑질(Enamel):** 바깥쪽의 흰색 층 (여기가 공격받습니다).
2.  **애니메이션 흐름 (발표 시나리오):**
    - **0~3초:** 붉은 점들($H^+$)이 비처럼 내려와 치아 표면에 쌓입니다. (산성 음료/음식 섭취 상황)
    - **3~6초:** 치아 표면이 덜컹거리고 높이가 낮아집니다. (부식 발생, 하이드록시아파타이트 용해)
    - **6~10초:** 파란색 반투명한 층이 그 위를 부드럽게 덮습니다. (발표 주제인 '새로운 코팅 물질'의 효과)

### 사용 방법

1.  위 코드를 복사하여 `tooth_ani.py`로 저장하세요.
2.  터미널에서 `python tooth_ani.py`를 실행하세요.
3.  애니메이션 창이 뜨면, 화면 캡처 프로그램(OBS 등)이나 PPT의 '화면 녹화' 기능을 이용해 동영상으로 저장하여 발표 자료에 넣으면 매우 효과적입니다.

**추가 팁:** 만약 더 "사실적인 질감(Texture)"을 원하신다면 Python 코드만으로는 한계가 있습니다. 그 경우에는 이 시뮬레이션을 보여주면서 **"Python으로 모델링한 부식 메커니즘 시뮬레이션입니다"**라고 멘트하는 것이 공학적/과학적 역량을 어필하기에 더 좋습니다.
