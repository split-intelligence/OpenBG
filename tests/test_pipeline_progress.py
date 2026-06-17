import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from engine.pipeline import build_output_path, remove_background


class PipelineProgressTests(unittest.TestCase):
    def test_build_output_path_uses_png_preview_name(self):
        self.assertEqual(build_output_path("portrait.jpg"), "portrait_nobg.png")
        self.assertEqual(build_output_path("portrait.jpeg"), "portrait_nobg.png")
        self.assertEqual(build_output_path("portrait.png"), "portrait_nobg.png")

    def test_remove_background_reports_honest_stage_progress(self):
        opened_image = object()
        saved_paths = []

        class FakeResult:
            def save(self, path):
                saved_paths.append(path)

        def fake_remove(image, **kwargs):
            self.assertIs(image, opened_image)
            self.assertEqual(kwargs["alpha_matting_foreground_threshold"], 270)
            self.assertEqual(kwargs["alpha_matting_background_threshold"], 15)
            return FakeResult()

        fake_image_module = SimpleNamespace(open=lambda path: opened_image)
        fake_pil = SimpleNamespace(Image=fake_image_module)
        fake_rembg = SimpleNamespace(remove=fake_remove)
        updates = []

        with patch.dict(
            sys.modules,
            {
                "PIL": fake_pil,
                "PIL.Image": fake_image_module,
                "rembg": fake_rembg,
            },
        ):
            output_path = remove_background("portrait.jpg", updates.append)

        self.assertEqual(output_path, "portrait_nobg.png")
        self.assertEqual(saved_paths, ["portrait_nobg.png"])
        self.assertEqual(
            [update.stage for update in updates],
            ["loading", "removing", "saving", "done"],
        )
        self.assertEqual([updates[0].percent, updates[2].percent, updates[3].percent], [12, 88, 100])
        self.assertTrue(updates[1].busy)
        self.assertIsNone(updates[1].percent)


if __name__ == "__main__":
    unittest.main()
