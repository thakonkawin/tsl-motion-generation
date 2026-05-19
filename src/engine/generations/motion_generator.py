class MotionGenerator:
    def __init__(self) -> None:
        pass
        # self._logger = Logger()

    # def search_gloss_sequence(self, glosses: list[str]) -> pd.DataFrame:
    #     filepath = AppConfig.ROOT_DIR / AppConfig.METADATA_PATH
    #     if not filepath.exists():
    #         msg = f"Path: {filepath}"
    #         self._logger.error(
    #             message=msg, module="GlossProcessor.search_gloss_sequence"
    #         )
    #         raise InvalidPathError(msg)

    #     df = pd.read_csv(filepath)

    #     # หา gloss ที่ไม่เจอ
    #     missing_glosses = [
    #         gloss for gloss in glosses if gloss not in set(df["gloss"].astype(str))
    #     ]

    #     # ต้องเจอทุกคำ
    #     if missing_glosses:
    #         msg = f"Missing_glosses: {missing_glosses}"
    #         self._logger.warn(
    #             message=msg, module="GlossProcessor.search_gloss_sequence"
    #         )
    #         raise ValueError(msg)

    #     # reorder ตาม input
    #     ordered_rows = []

    #     for gloss in glosses:
    #         row = df[df["gloss"] == gloss]

    #         if row.empty:
    #             msg = f"Gloss not found: {gloss}"
    #             self._logger.error(
    #                 message=msg, module="GlossProcessor.search_gloss_sequence"
    #             )
    #             raise ValueError(msg)

    #         ordered_rows.append(row.iloc[0])

    #     result = pd.DataFrame(ordered_rows).reset_index(drop=True)

    #     return result

    # def generate_sentence_motion(self, gloss_sequence: pd.DataFrame) -> None:

    #     motion_data = self._set_frame_transition(data=gloss_sequence)

    #     motion_id = str(uuid.uuid4())

    #     motion_folder = AppConfig.ROOT_DIR / AppConfig.MOTION_SENTENCE_DIR
    #     motion_folder.mkdir(parents=True, exist_ok=True)

    #     frame_number = 0

    #     with h5py.File(AppConfig.ROOT_DIR / AppConfig.DATASET_PATH, "r") as f:
    #         for _, row in motion_data.iterrows():
    #             sign_id = str(row["sign_id"])

    #             group = cast(h5py.Group, f[sign_id])

    #             vertices_group = group["vertices"]

    #             start_frame = cast(int, row["frame_start"])
    #             end_frame = cast(int, row["frame_end"])
    #             frame_rate = cast(int, row["fps"])
    #             # loop ตามช่วง START-END
    #             for frame_idx in range(start_frame, end_frame):
    #                 smplx_params = {}

    #                 for param_name in vertices_group.keys():
    #                     # ใช้ frame เดียวกันทุก param
    #                     param_data = vertices_group[param_name][frame_idx]

    #                     param_data = np.expand_dims(param_data, axis=0)

    #                     smplx_params[param_name] = param_data

    #                 smplx_params["gender"] = "neutral"

    #                 motion_path = PathManager.get_motion_path(motion_id, frame_number)

    #                 dump_pkl(motion_path, smplx_params)

    #                 frame_number += 1

    #     result = [motion_id, frame_rate, frame_number]

    #     return result
