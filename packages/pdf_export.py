import time
from fpdf import FPDF
import handicapEGA as ega


def export_scorecard(course: dict, hci: float, pcc: int, filepath: str):
    """Generates a Scorecard as PDF and outputs it to given filepath

    Args:
        course (dict): The Course being played on
        hci (float): The Handicap Index of the player
        pcc (int): PCC or CBA of the game
        filepath (str): The location and filename the scorecard should be saved to
    """
    # TODO: zuletzt verwendete eingaben nehmen
    data = prepare_table_data(course, hci, pcc)
    # create pdf page
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Comic Sans", size=12)

    date = time.time()
    pdf.cell(
        text=f"__*CR:* {course["course_rating"]} *SR:*{course["slope_rating"]} *PCC/CBA:*{pcc} *Datum:*{date} *HCI:*{hci} *Name:*\t\t__",
        markdown=True,
    )

    with pdf.table() as table:
        for data_row in data:
            row = table.row()
            for cell in data_row:
                row.cell(cell)

    pdf.output(filepath)
    # TODO: irgendwas damit UI "ok" sagen kann


def prepare_table_data(
    course: dict, hci: float, pcc: int
) -> tuple[tuple[str, str, str, str, str], ...]:
    """Generates a tuple of tuples representing rows in the scorecard table

    Args:
        course (dict): The course played on
        hci (float): The handicap of the player
        pcc (int): PCC/CBA of the game

    Returns:
        tuple[tuple[str, str, str, str, str], ...]:
        A tuple of tuples representing the rows of the table
    """
    hc_strokes = ega.playingHandicap(
        True, hci, course["course_rating"], course["slope_rating"], course["par"]
    )
    stroke_allocation = [
        x - y
        for x, y in zip(ega.spreadPlayingHC(course, hc_strokes, True), course["par"])
    ]
    # Hole#, Par, HCP, hcp-strokes, shots taken (empty)
    rows = ()
    for i in range(0, 9):
        row = tuple(
            map(
                str,
                (
                    i + 1,
                    course["par"][i],
                    course["handicap_stroke_index"][i],
                    stroke_allocation[i] * "/",
                    "",
                ),
            )
        )
        rows += row
    rows += ("OUT", sum(course["par"][0:9]), "", "", "")

    for i in range(9, 18):
        row = tuple(
            map(
                str,
                (
                    i + 1,
                    course["par"][i],
                    course["handicap_stroke_index"][i],
                    stroke_allocation[i] * "/",
                    "",
                ),
            )
        )
        rows += row
    rows += ("IN", sum(course["par"][9:18]), "", "", "")
    rows += ("GESAMT", sum(course["par"]), "", "", "")

    return rows
