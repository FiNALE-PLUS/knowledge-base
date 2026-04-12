from slide_datatypes import SlidePattern, SlideParams, SDTRowWithMetadata

import glob
from pathlib import Path
import sqlite3

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats
import seaborn as sns


def get_clockwise_slide_distance(start_location: int, end_location: int) -> int:
    return abs(start_location - end_location)


def get_counter_clockwise_slide_distance(start_location: int, end_location: int) -> int:
    return 7 - abs(start_location - end_location)


def get_shortest_slide_distance(start_location: int, end_location: int) -> int:
    return min(
        get_clockwise_slide_distance(start_location, end_location),
        get_counter_clockwise_slide_distance(start_location, end_location)
    )


def get_distance_for_slide(start_location: int, end_location: int, slide_pattern: SlidePattern) -> int:
    match slide_pattern.value:
        case SlidePattern.no_slide.value:
            raise ValueError('`no_slide` cannot be used to calculate slide cw_distance.')

        case SlidePattern.straight.value:
            return get_shortest_slide_distance(start_location, end_location)

        case SlidePattern.ccw_edge.value:
            return get_counter_clockwise_slide_distance(start_location, end_location)

        case SlidePattern.cw_edge.value:
            return get_clockwise_slide_distance(start_location, end_location)

        case SlidePattern.ccw_centre_arc.value:
            return get_counter_clockwise_slide_distance(start_location, end_location)

        case SlidePattern.cw_centre_arc.value:
            return get_clockwise_slide_distance(start_location, end_location)

        case SlidePattern.zigzag_s.value | SlidePattern.zigzag_z.value:
            return get_shortest_slide_distance(start_location, end_location)

        case SlidePattern.straight_centre_end.value:
            return get_shortest_slide_distance(start_location, end_location)

        case SlidePattern.straight_centre_ccw_end.value:
            return get_counter_clockwise_slide_distance(start_location, end_location)

        case SlidePattern.straight_centre_cw_end.value:
            return get_clockwise_slide_distance(start_location, end_location)

        case SlidePattern.ccw_grand_v.value:
            return get_counter_clockwise_slide_distance(start_location, end_location)

        case SlidePattern.cw_grand_v.value:
            return get_clockwise_slide_distance(start_location, end_location)

        case SlidePattern.fan.value:
            return get_shortest_slide_distance(start_location, end_location)

    raise ValueError(f'Unrecognized slide pattern_group type {slide_pattern} {type(slide_pattern)}.')


# Exclude utage chart files, and exclude SRT
plain_non_utage_charts = glob.glob("plain charts/*_0[123456]*.s[cdz]t")

# sdt_pattern = re.compile(r"")
df = pd.DataFrame(columns=["star_duration", "slide_duration", "cw_distance", "slide_pattern", "difficulty", "version"])

notes: list[SDTRowWithMetadata] = []

slide_params: list[SlideParams] = []


with sqlite3.connect('table_data.sqlite') as conn:
    for chart in plain_non_utage_charts:
        chart_path = Path(chart)

        chart_difficulty = int(chart_path.stem.split("_")[-1])
        song_id = int(chart_path.stem.split("_")[0])
        # print(chart_path.stem)
        # print(song_id)
        chart_bpm = conn.execute("""SELECT bpm FROM song WHERE id = ?;""", (song_id,)).fetchone()

        if chart_bpm:
            chart_bpm = chart_bpm[0]

        with open(chart_path, "r") as f:
            chart_lines = f.readlines()
            # Get all components of the chart, remove whitespace and empty sets from blank lines
            chart_component_sets = [
                [str.strip(component) for component in chart_line.split(',') if str.strip(component)]
                for chart_line in chart_lines if str.strip(chart_line)
            ]

            rows = []

            chart_version = chart_path.suffix[1:]
            chart_difficulty = int(chart_path.stem.split("_")[-1])

            match chart_path.suffix:
                case ".sdt":
                    rows = [SDTRowWithMetadata(whole_measure=row[0], fractional_measure=row[1], duration=row[2], location=row[3],
                                               note_type=row[4],
                                               slide_id=row[5], slide_pattern=row[6], slide_amount=row[7], slide_delay=row[8],
                                               difficulty=chart_difficulty, bpm=chart_bpm)
                            for row in chart_component_sets]

                case ".sct":
                    rows = [SDTRowWithMetadata(whole_measure=row[0], fractional_measure=row[1], duration=row[2], location=row[3],
                                               note_type=row[4],
                                               slide_id=row[5], slide_pattern=row[6], slide_amount=row[7], slide_delay=0.25,
                                               difficulty=chart_difficulty, bpm=chart_bpm)
                            for row in chart_component_sets]

                case ".szt":
                    rows = [SDTRowWithMetadata(whole_measure=row[0], fractional_measure=row[1], duration=row[2], location=row[3],
                                               note_type=row[4],
                                               slide_id=row[5], slide_pattern=row[6], slide_amount=1, slide_delay=0.25,
                                               difficulty=chart_difficulty, bpm=chart_bpm)
                            for row in chart_component_sets]

            for potential_star in rows:
                if potential_star.note_type == 4 or potential_star.note_type == 5:
                    slides_param_sets: list[SlideParams] = []

                    slides = [i for i in rows if i.note_type == 0
                              and i.whole_measure == potential_star.whole_measure
                              and i.fractional_measure == potential_star.fractional_measure]

                    for slide in slides:
                        end_slide = [i for i in rows if i.note_type == 128 and i.slide_id == slide.slide_id]
                        # Each start slide should have only one end slide
                        assert len(end_slide) == 1

                        end_slide = end_slide[0]

                        slides_param_sets.append(SlideParams(
                            star_duration=potential_star.duration,
                            slide_duration=slide.duration,
                            cw_distance=get_clockwise_slide_distance(
                                potential_star.location, end_slide.location
                            ),
                            ccw_distance=get_counter_clockwise_slide_distance(
                                potential_star.location, end_slide.location
                            ),
                            closest_distance=get_shortest_slide_distance(
                                potential_star.location, end_slide.location
                            ),
                            slide_pattern=slide.slide_pattern,
                            version=chart_version,
                            slide_delay=slide.slide_delay,

                            difficulty=potential_star.difficulty,
                            bpm=potential_star.bpm
                        ))

                    slide_params.extend(slides_param_sets)

                notes.extend(rows)

# Get all slides found in the game as a single dataframe
full_df = pd.DataFrame(
    data=[
        [params.star_duration, params.slide_duration, params.slide_delay, params.cw_distance,
         params.slide_pattern, params.bpm, params.difficulty, params.version]
        for params in slide_params],
    columns=["star_duration", "slide_duration", "slide_delay", "cw_distance", "pattern_group", "bpm", "difficulty", "version"]
)
# Remove duplicates to find patterns between different configurations over huge groups of identical slide
pruned_df = full_df.drop_duplicates()

pruned_df['duration_ratio']            = pruned_df['star_duration'] / pruned_df['slide_duration']
pruned_df['duration_with_delay']       = pruned_df['slide_duration'] + pruned_df['slide_delay']
pruned_df['duration_with_delay_ratio'] = pruned_df['star_duration'] / pruned_df['duration_with_delay']