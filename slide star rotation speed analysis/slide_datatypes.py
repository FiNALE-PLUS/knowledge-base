from enum import IntEnum

from typing import Literal

from pydantic import BaseModel, Field

difficulty_colours = {
    1: '#00afff',
    2: '#00e800',
    3: '#ff9400',
    4: '#ff0519',
    5: '#b300ff',
    6: '#f6c9ff',
}


class SlidePattern(IntEnum):
    no_slide = 0
    straight = 1
    ccw_edge = 2
    cw_edge = 3
    ccw_centre_arc = 4
    cw_centre_arc = 5
    zigzag_s = 6
    zigzag_z = 7
    straight_centre_end = 8
    straight_centre_ccw_end = 9
    straight_centre_cw_end = 10
    ccw_grand_v = 11
    cw_grand_v = 12
    fan = 13


class ChartDifficulty(IntEnum):
    easy = 1
    basic = 2
    advanced = 3
    expert = 4
    master = 5
    re_master = 6


class SDTRowWithMetadata(BaseModel):
    whole_measure: int = Field(ge=0)
    fractional_measure: float = Field(ge=0, le=1) # SCT Can have this as 1, look into this
    duration: float = Field(ge=0)
    location: int = Literal[0, 1, 2, 3, 4, 5, 6, 7]
    note_type: int = Literal[0, 1, 2, 3, 4, 5, 128]
    slide_id: int = Field(ge=0)
    slide_pattern: SlidePattern
    slide_amount: int = Field(ge=0)
    slide_delay: float = Field(ge=0)

    difficulty: ChartDifficulty
    bpm: float | None


class SlideParams(BaseModel):
    star_duration: float = Field(ge=0)
    slide_duration: float = Field(ge=0)
    slide_delay: float = Field(ge=0)
    cw_distance: int = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8]
    ccw_distance: int = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8]
    closest_distance: int = Literal[0, 1, 2, 3, 4]
    # end: int = Literal[0, 1, 2, 3, 4, 5, 6, 7]
    slide_pattern: SlidePattern
    bpm: float | None
    difficulty: ChartDifficulty
    version: str