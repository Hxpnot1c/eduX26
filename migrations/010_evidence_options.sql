-- How many options a multiple-choice question showed (tune-from-research). With bkt.mcq_guess_from_options,
-- its guess is 1 / n_options. Null for open answers and for rows written before this: they keep the type's guess.
ALTER TABLE evidence_log ADD COLUMN n_options INTEGER;
