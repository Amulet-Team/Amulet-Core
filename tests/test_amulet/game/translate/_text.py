import unittest

from amulet.game.translate._functions._code_functions._text import (
    RawTextComponent,
    RawTextFormatting,
    ExtendedBedrockSectionParser,
    Colour,
)


class ColourTestCase(unittest.TestCase):
    def test_init(self) -> None:
        colour = Colour(1, 2, 3)
        self.assertEqual(1, colour.r)
        self.assertEqual(2, colour.g)
        self.assertEqual(3, colour.b)

    def test_equal(self) -> None:
        self.assertEqual(Colour(1, 2, 3), Colour(1, 2, 3))
        self.assertNotEqual(Colour(1, 2, 3), Colour(10, 2, 3))
        self.assertNotEqual(Colour(1, 2, 3), Colour(1, 20, 3))
        self.assertNotEqual(Colour(1, 2, 3), Colour(1, 2, 30))

    def test_hash(self) -> None:
        self.assertEqual(hash(Colour(1, 2, 3)), hash(Colour(1, 2, 3)))
        self.assertNotEqual(hash(Colour(1, 2, 3)), hash(Colour(10, 2, 3)))
        self.assertNotEqual(hash(Colour(1, 2, 3)), hash(Colour(1, 20, 3)))
        self.assertNotEqual(hash(Colour(1, 2, 3)), hash(Colour(1, 2, 30)))


class RawTextFormattingTestCase(unittest.TestCase):
    def test_init(self) -> None:
        formatting = RawTextFormatting()
        self.assertIs(None, formatting.colour)
        self.assertIs(None, formatting.bold)
        self.assertIs(None, formatting.italic)
        self.assertIs(None, formatting.underlined)
        self.assertIs(None, formatting.strikethrough)
        self.assertIs(None, formatting.obfuscated)

        formatting.colour = Colour(1, 2, 3)
        self.assertEqual(Colour(1, 2, 3), formatting.colour)
        formatting.bold = True
        self.assertTrue(formatting.bold)
        formatting.italic = True
        self.assertTrue(formatting.italic)
        formatting.underlined = True
        self.assertTrue(formatting.underlined)
        formatting.strikethrough = True
        self.assertTrue(formatting.strikethrough)
        formatting.obfuscated = True
        self.assertTrue(formatting.obfuscated)

        formatting = RawTextFormatting(
            colour=Colour(1, 2, 3),
            italic=True,
            strikethrough=True,
        )
        self.assertEqual(Colour(1, 2, 3), formatting.colour)
        self.assertIs(None, formatting.bold)
        self.assertTrue(formatting.italic)
        self.assertIs(None, formatting.underlined)
        self.assertTrue(formatting.strikethrough)
        self.assertIs(None, formatting.obfuscated)

        formatting = RawTextFormatting(
            bold=True,
            underlined=True,
            obfuscated=True,
        )
        self.assertIs(
            None,
            formatting.colour,
        )
        self.assertTrue(formatting.bold)
        self.assertIs(None, formatting.italic)
        self.assertTrue(formatting.underlined)
        self.assertIs(None, formatting.strikethrough)
        self.assertTrue(formatting.obfuscated)

    def test_equal(self) -> None:
        self.assertEqual(RawTextFormatting(), RawTextFormatting())
        formatting = RawTextFormatting(
            colour=Colour(1, 2, 3),
            bold=True,
            italic=True,
            underlined=True,
            strikethrough=True,
            obfuscated=True,
        )
        self.assertEqual(formatting, formatting)


class TextTestCase(unittest.TestCase):
    def test_init(self) -> None:
        component = RawTextComponent()
        self.assertEqual("", component.text)
        self.assertEqual(RawTextFormatting(), component.formatting)
        self.assertEqual([], component.children)

        component = RawTextComponent("a")
        self.assertEqual("a", component.text)
        self.assertEqual(RawTextFormatting(), component.formatting)
        self.assertEqual([], component.children)

        component = RawTextComponent(
            "a",
            RawTextFormatting(Colour(1, 1, 1), bold=True),
            children=[RawTextComponent("b")],
        )
        self.assertEqual("a", component.text)
        self.assertEqual(
            RawTextFormatting(Colour(1, 1, 1), bold=True),
            component.formatting,
        )
        self.assertEqual([RawTextComponent("b")], component.children)

    def test_equal(self) -> None:
        self.assertEqual(
            RawTextComponent(),
            RawTextComponent(),
        )

        self.assertEqual(
            RawTextComponent("a"),
            RawTextComponent("a"),
        )

        self.assertNotEqual(
            RawTextComponent("a"),
            RawTextComponent("b"),
        )

        self.assertEqual(
            RawTextComponent("a", RawTextFormatting(italic=True)),
            RawTextComponent("a", RawTextFormatting(italic=True)),
        )

        self.assertNotEqual(
            RawTextComponent("a", RawTextFormatting(italic=True)),
            RawTextComponent("a", RawTextFormatting(italic=False)),
        )

        self.assertNotEqual(
            RawTextComponent(children=[]),
            RawTextComponent(children=[RawTextComponent()]),
        )

    def test_to_section_text(self) -> None:
        self.assertEqual(
            "",
            RawTextComponent().to_section_text(ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            "test",
            RawTextComponent("test").to_section_text(ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            "§ktest",
            RawTextComponent(
                "test", RawTextFormatting(obfuscated=True)
            ).to_section_text(ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            "§ltest",
            RawTextComponent("test", RawTextFormatting(bold=True)).to_section_text(
                ExtendedBedrockSectionParser
            ),
        )

        # Bedrock does not support strikethrough or underlined
        self.assertEqual(
            "test",
            RawTextComponent(
                "test", RawTextFormatting(strikethrough=True)
            ).to_section_text(ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            "test",
            RawTextComponent(
                "test", RawTextFormatting(underlined=True)
            ).to_section_text(ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            "§otest",
            RawTextComponent("test", RawTextFormatting(italic=True)).to_section_text(
                ExtendedBedrockSectionParser
            ),
        )

        self.assertEqual(
            "§l§o§ktest",
            RawTextComponent(
                "test",
                RawTextFormatting(
                    None,
                    True,
                    True,
                    True,
                    True,
                    True,
                ),
            ).to_section_text(ExtendedBedrockSectionParser),
        )

        for colour, code in ExtendedBedrockSectionParser.Colour2Code.items():
            with self.subTest(str(colour)):
                self.assertEqual(
                    f"§{code}test",
                    RawTextComponent(
                        "test", RawTextFormatting(colour=colour)
                    ).to_section_text(ExtendedBedrockSectionParser),
                )

        for colour, code in ExtendedBedrockSectionParser.Colour2Code.items():
            with self.subTest(str(colour)):
                self.assertEqual(
                    f"§l§o§k§{code}test",
                    RawTextComponent(
                        "test",
                        RawTextFormatting(
                            colour,
                            True,
                            True,
                            True,
                            True,
                            True,
                        ),
                    ).to_section_text(ExtendedBedrockSectionParser),
                )

        # Test child behaviour
        self.assertEqual(
            "§ctesttesttest",
            RawTextComponent(
                "test",
                RawTextFormatting(Colour(255, 85, 85)),
                [RawTextComponent("test"), RawTextComponent("test")],
            ).to_section_text(ExtendedBedrockSectionParser),
        )
        self.assertEqual(
            "§ctest§1test§ctest",
            RawTextComponent(
                "test",
                RawTextFormatting(Colour(255, 85, 85)),
                [
                    RawTextComponent("test", RawTextFormatting(Colour(0, 0, 170))),
                    RawTextComponent("test"),
                ],
            ).to_section_text(ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            "§ctesttest",
            RawTextComponent(
                children=[
                    RawTextComponent("test", RawTextFormatting(Colour(255, 85, 85))),
                    RawTextComponent("test", RawTextFormatting(Colour(255, 85, 85))),
                ],
            ).to_section_text(ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            "§ctest§1test",
            RawTextComponent(
                children=[
                    RawTextComponent("test", RawTextFormatting(Colour(255, 85, 85))),
                    RawTextComponent("test", RawTextFormatting(Colour(0, 0, 170))),
                ],
            ).to_section_text(ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            "§ltest§r§otest",
            RawTextComponent(
                children=[
                    RawTextComponent("test", RawTextFormatting(bold=True)),
                    RawTextComponent(
                        "test", RawTextFormatting(bold=False, italic=True)
                    ),
                ],
            ).to_section_text(ExtendedBedrockSectionParser),
        )

    def test_from_section_text(self) -> None:
        self.assertEqual(
            RawTextComponent(),
            RawTextComponent.from_section_text("", ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            RawTextComponent("test"),
            RawTextComponent.from_section_text("test", ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            RawTextComponent("test", RawTextFormatting(obfuscated=True)),
            RawTextComponent.from_section_text("§ktest", ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            RawTextComponent("test", RawTextFormatting(bold=True)),
            RawTextComponent.from_section_text("§ltest", ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            RawTextComponent("test", RawTextFormatting(Colour(151, 22, 7))),
            RawTextComponent.from_section_text("§mtest", ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            RawTextComponent("test", RawTextFormatting(Colour(180, 104, 77))),
            RawTextComponent.from_section_text("§ntest", ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            RawTextComponent("test", RawTextFormatting(italic=True)),
            RawTextComponent.from_section_text("§otest", ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            RawTextComponent("test", RawTextFormatting(bold=True)),
            RawTextComponent.from_section_text("§ltest", ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            RawTextComponent(
                "test",
                RawTextFormatting(None, False, False, False, False, False),
            ),
            RawTextComponent.from_section_text("§rtest", ExtendedBedrockSectionParser),
        )

        self.assertEqual(
            RawTextComponent(
                "test",
                RawTextFormatting(
                    None,
                    True,
                    True,
                    None,
                    None,
                    True,
                ),
            ),
            RawTextComponent.from_section_text(
                "§l§o§ktest", ExtendedBedrockSectionParser
            ),
        )

        for colour, code in ExtendedBedrockSectionParser.Colour2Code.items():
            with self.subTest(str(colour)):
                self.assertEqual(
                    RawTextComponent(
                        "test",
                        RawTextFormatting(colour),
                    ),
                    RawTextComponent.from_section_text(
                        f"§{code}test", ExtendedBedrockSectionParser
                    ),
                )

        for colour, code in ExtendedBedrockSectionParser.Colour2Code.items():
            with self.subTest(str(colour)):
                self.assertEqual(
                    RawTextComponent(
                        "test",
                        RawTextFormatting(
                            colour,
                            True,
                            True,
                            None,
                            None,
                            True,
                        ),
                    ),
                    RawTextComponent.from_section_text(
                        f"§l§o§k§{code}test", ExtendedBedrockSectionParser
                    ),
                )

        # Test child behaviour
        self.assertEqual(
            RawTextComponent(
                "testtesttest",
                RawTextFormatting(Colour(255, 85, 85)),
            ),
            RawTextComponent.from_section_text(
                "§ctesttesttest", ExtendedBedrockSectionParser
            ),
        )
        self.assertEqual(
            RawTextComponent(
                children=[
                    RawTextComponent("test", RawTextFormatting(Colour(255, 85, 85))),
                    RawTextComponent("test", RawTextFormatting(Colour(0, 0, 170))),
                    RawTextComponent("test", RawTextFormatting(Colour(255, 85, 85))),
                ]
            ),
            RawTextComponent.from_section_text(
                "§ctest§1test§ctest", ExtendedBedrockSectionParser
            ),
        )

        self.assertEqual(
            RawTextComponent("testtest", RawTextFormatting(Colour(255, 85, 85))),
            RawTextComponent.from_section_text(
                "§ctesttest", ExtendedBedrockSectionParser
            ),
        )

        self.assertEqual(
            RawTextComponent(
                children=[
                    RawTextComponent("test", RawTextFormatting(Colour(255, 85, 85))),
                    RawTextComponent("test", RawTextFormatting(Colour(0, 0, 170))),
                ],
            ),
            RawTextComponent.from_section_text(
                "§ctest§1test", ExtendedBedrockSectionParser
            ),
        )

        self.assertEqual(
            RawTextComponent(
                children=[
                    RawTextComponent("test", RawTextFormatting(bold=True)),
                    RawTextComponent(
                        "test",
                        RawTextFormatting(
                            None,
                            False,
                            True,
                            False,
                            False,
                            False,
                        ),
                    ),
                ],
            ),
            RawTextComponent.from_section_text(
                "§ltest§r§otest", ExtendedBedrockSectionParser
            ),
        )

    def test_newline_split(self) -> None:
        self.assertEqual(
            [RawTextComponent("test"), RawTextComponent("test")],
            RawTextComponent.from_section_text(
                "test\ntest", ExtendedBedrockSectionParser, True
            ),
        )

        self.assertEqual(
            [
                RawTextComponent("test", RawTextFormatting(Colour(255, 85, 85))),
                RawTextComponent("test", RawTextFormatting(Colour(85, 255, 85))),
            ],
            RawTextComponent.from_section_text(
                "§ctest\n§atest", ExtendedBedrockSectionParser, True
            ),
        )

        self.assertEqual(
            [
                RawTextComponent("test", RawTextFormatting(Colour(255, 85, 85))),
                RawTextComponent("test", RawTextFormatting(Colour(85, 255, 85))),
            ],
            RawTextComponent.from_section_text(
                "§ctest§a\ntest", ExtendedBedrockSectionParser, True
            ),
        )

    def test_from_raw_text(self) -> None:
        self.assertEqual(
            RawTextComponent(
                "A", children=[RawTextComponent("B"), RawTextComponent("C")]
            ),
            RawTextComponent.from_java_raw_text(["A", "B", "C"]),
        )

        self.assertEqual(
            RawTextComponent(
                "A",
                RawTextFormatting(Colour(0xFF, 0x55, 0x55)),
                [RawTextComponent("B"), RawTextComponent("C")],
            ),
            RawTextComponent.from_java_raw_text(
                [{"text": "A", "color": "red"}, "B", "C"]
            ),
        )

        self.assertEqual(
            RawTextComponent("A", RawTextFormatting(Colour(0x01, 0x02, 0x03))),
            RawTextComponent.from_java_raw_text({"text": "A", "color": "#010203"}),
        )

        self.assertEqual(
            RawTextComponent("A", RawTextFormatting(bold=True)),
            RawTextComponent.from_java_raw_text({"text": "A", "bold": True}),
        )
        self.assertEqual(
            RawTextComponent("A", RawTextFormatting(italic=True)),
            RawTextComponent.from_java_raw_text({"text": "A", "italic": True}),
        )
        self.assertEqual(
            RawTextComponent("A", RawTextFormatting(underlined=True)),
            RawTextComponent.from_java_raw_text({"text": "A", "underlined": True}),
        )
        self.assertEqual(
            RawTextComponent("A", RawTextFormatting(strikethrough=True)),
            RawTextComponent.from_java_raw_text({"text": "A", "strikethrough": True}),
        )
        self.assertEqual(
            RawTextComponent("A", RawTextFormatting(obfuscated=True)),
            RawTextComponent.from_java_raw_text({"text": "A", "obfuscated": True}),
        )

    def test_to_raw_text(self) -> None:
        self.assertEqual(
            {"text": "A", "extra": ["B", "C"]},
            RawTextComponent(
                "A", children=[RawTextComponent("B"), RawTextComponent("C")]
            ).to_java_raw_text(),
        )

        self.assertEqual(
            {"text": "A", "color": "red", "extra": ["B", "C"]},
            RawTextComponent(
                "A",
                RawTextFormatting(Colour(0xFF, 0x55, 0x55)),
                [RawTextComponent("B"), RawTextComponent("C")],
            ).to_java_raw_text(),
        )

        self.assertEqual(
            {"text": "A", "color": "#010203"},
            RawTextComponent(
                "A", RawTextFormatting(Colour(0x01, 0x02, 0x03))
            ).to_java_raw_text(),
        )

        self.assertEqual(
            {"text": "A", "bold": True},
            RawTextComponent("A", RawTextFormatting(bold=True)).to_java_raw_text(),
        )
        self.assertEqual(
            {"text": "A", "italic": True},
            RawTextComponent("A", RawTextFormatting(italic=True)).to_java_raw_text(),
        )
        self.assertEqual(
            {"text": "A", "underlined": True},
            RawTextComponent(
                "A", RawTextFormatting(underlined=True)
            ).to_java_raw_text(),
        )
        self.assertEqual(
            {"text": "A", "strikethrough": True},
            RawTextComponent(
                "A", RawTextFormatting(strikethrough=True)
            ).to_java_raw_text(),
        )
        self.assertEqual(
            {"text": "A", "obfuscated": True},
            RawTextComponent(
                "A", RawTextFormatting(obfuscated=True)
            ).to_java_raw_text(),
        )


if __name__ == "__main__":
    unittest.main()
