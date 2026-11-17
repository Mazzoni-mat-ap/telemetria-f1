import unittest
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from funcoes_telemetria import (
    calcular_energia_frenagem,
    comparar_mapas_g_longitudinal,
    mapa_g_longitudinal,
)


class TelemetryFunctionTests(unittest.TestCase):
    def test_braking_energy_uses_acceleration_sample_distances(self):
        telemetry = pd.DataFrame({
            "Distance": [0, 10, 30, 60, 100],
            "Speed": [120, 110, 100, 70, 40],
        })
        filtered_distances = np.array([10, 30, 60, 100])
        smoothed_g = np.array([0, -1, -1, 0])

        with patch(
            "funcoes_telemetria.calcular_g_longitudinal",
            return_value=(filtered_distances, smoothed_g, smoothed_g),
        ):
            zones = calcular_energia_frenagem(telemetry, duracao_minima_pontos=1)

        self.assertEqual(zones.iloc[0]["distancia_inicio"], 30)
        self.assertEqual(zones.iloc[0]["distancia_fim"], 100)
        self.assertAlmostEqual(zones.iloc[0]["v_inicial_kmh"], 100)
        self.assertAlmostEqual(zones.iloc[0]["v_final_kmh"], 40)

    def test_longitudinal_maps_align_values_with_line_segments(self):
        telemetry = pd.DataFrame({
            "Distance": [0, 1, 2, 3],
            "Speed": [100, 110, 120, 130],
            "X": [0, 1, 2, 3],
            "Y": [0, 1, 0, -1],
        })
        distances = telemetry["Distance"].to_numpy()
        longitudinal_g = np.array([0.0, 1.0, -1.0, 0.5])

        with patch(
            "funcoes_telemetria.calcular_g_longitudinal",
            return_value=(distances, longitudinal_g, longitudinal_g),
        ):
            figures = [
                mapa_g_longitudinal(telemetry),
                comparar_mapas_g_longitudinal(telemetry, telemetry, "A", "B"),
            ]

        try:
            for figure, axes_count in zip(figures, [1, 2]):
                for axis in figure.axes[:axes_count]:
                    collection = axis.collections[0]
                    self.assertEqual(
                        len(collection.get_segments()), collection.get_array().size
                    )
        finally:
            for figure in figures:
                plt.close(figure)


if __name__ == "__main__":
    unittest.main()
