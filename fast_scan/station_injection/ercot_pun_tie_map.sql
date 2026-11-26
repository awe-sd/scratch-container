-- ============================================================================
-- AWDEV.ERCOTRT.ERCOTPUNTIEMAP
--
-- (PUN station, real ERCOT-side neighbour) crosswalk for the PUN back-out.
-- Grain: DISTINCT (PUNSTATION, NEIGHBORSTATION); NOT_ESTIMABLE PUNs get one
-- row with NULL neighbour/group. NEIGHBORGROUPID = PUNSTATION except for
-- ENTANGLED_GROUP pairs, which share one group id (union of real neighbours).
-- METHODTAG/counts match PUN_BACKOUT_FINDINGS.md Section 5 exactly:
-- EXACT_SWITCHING (8), DAM_LOAD_ADJUSTED (24), ENTANGLED_GROUP (12/6 pairs),
-- NOT_ESTIMABLE (12). Crosswalk verification, gen-chain check, and the
-- 2026-09-25 grading-gate fixes: SESSION_HANDOFF.md, "PUN injection loader".
-- ============================================================================

CREATE OR REPLACE TABLE AWDEV.ERCOTRT.ERCOTPUNTIEMAP (
    PUNSTATION      VARCHAR(30)   NOT NULL,
    NEIGHBORSTATION VARCHAR(30),                 -- NULL only for NOT_ESTIMABLE inventory rows
    NEIGHBORGROUPID VARCHAR(30),                 -- NULL only for NOT_ESTIMABLE inventory rows
    METHODTAG       VARCHAR(30)   NOT NULL,
    KVLEVELS        VARCHAR(50),
    NOTE            VARCHAR(500)
);

INSERT INTO AWDEV.ERCOTRT.ERCOTPUNTIEMAP
    (PUNSTATION, NEIGHBORSTATION, NEIGHBORGROUPID, METHODTAG, KVLEVELS, NOTE)
VALUES
('AK', 'HUD', 'HUD', 'ENTANGLED_GROUP', '138', 'Entangled group ''HUD'': shares real neighbour(s) with MSN; group figure only, not individually attributable.'),
('AMOCOOIL', 'GRNBELT', 'AMOCOOIL', 'EXACT_SWITCHING', '138', NULL),
('ARC', NULL, NULL, 'NOT_ESTIMABLE', '138', 'N_TIES=1 (PSA); folds into PSA''s LY-group combined figure.'),
('BBP', 'PWL', 'BBP', 'DAM_LOAD_ADJUSTED', '13;138', 'N_TIES=3 > N_REAL_NEIGHBORS=1: parallel ties to the same neighbour(s), deduplicated here.'),
('BFM', 'LP', 'BFM', 'DAM_LOAD_ADJUSTED', '138', NULL),
('BFM', 'MIRAGE', 'BFM', 'DAM_LOAD_ADJUSTED', '138', NULL),
('BSF', 'BZ', 'BSF', 'DAM_LOAD_ADJUSTED', '138', NULL),
('BSF', 'HN', 'BSF', 'DAM_LOAD_ADJUSTED', '138', NULL),
('BTE', 'CHB', 'BTE', 'EXACT_SWITCHING', '345', NULL),
('BYU', 'MCB', 'BYU', 'DAM_LOAD_ADJUSTED', '13;138', 'N_TIES=5 > N_REAL_NEIGHBORS=3: parallel ties to the same neighbour(s), deduplicated here.'),
('BYU', 'ORION', 'BYU', 'DAM_LOAD_ADJUSTED', '13;138', 'N_TIES=5 > N_REAL_NEIGHBORS=3: parallel ties to the same neighbour(s), deduplicated here.'),
('BYU', 'SBK', 'BYU', 'DAM_LOAD_ADJUSTED', '13;138', 'N_TIES=5 > N_REAL_NEIGHBORS=3: parallel ties to the same neighbour(s), deduplicated here.'),
('CAL', NULL, NULL, 'NOT_ESTIMABLE', '138', 'N_TIES=1 (PL); folds into PL''s own figure (own SCED gross ~99.9 MW already inside PL''s I_PUN).'),
('CARBN', 'BSPSW', 'CARBN', 'DAM_LOAD_ADJUSTED', '69', NULL),
('CARBN', 'COHMA', 'CARBN', 'DAM_LOAD_ADJUSTED', '69', NULL),
('CCEC', 'CITGO_NO', 'CCEC', 'EXACT_SWITCHING', '138', NULL),
('CELANEBI', 'KLEBERG', 'CELANEBI', 'DAM_LOAD_ADJUSTED', '138', NULL),
('CELANEBI', 'N_SHARPE', 'CELANEBI', 'DAM_LOAD_ADJUSTED', '138', NULL),
('CHE', 'DPW', 'DPW', 'ENTANGLED_GROUP', '138;345', 'Entangled group ''DPW'': shares real neighbour(s) with LYD; group figure only, not individually attributable.'),
('COPSUB10', NULL, NULL, 'NOT_ESTIMABLE', '138', 'N_TIES=2 (CPCSUB9, P66SUB12); part of COPSUB8->CPCSUB9->COPSUB10->P66SUB12 isolated chain, exits via SCLPCOGN (PHILLPS2 group).'),
('COPSUB8', NULL, NULL, 'NOT_ESTIMABLE', '138', 'N_TIES=2 (CPCSUB9, SCLPCOGN); part of COPSUB8->CPCSUB9->COPSUB10->P66SUB12 isolated chain that exits the SE-visible grid only through SCLPCOGN (PHILLPS2 group).'),
('CPCSUB9', NULL, NULL, 'NOT_ESTIMABLE', '138', 'N_TIES=2 (COPSUB10, COPSUB8); part of COPSUB8->CPCSUB9->COPSUB10->P66SUB12 isolated chain, exits via SCLPCOGN (PHILLPS2 group).'),
('CSUNGATE', NULL, NULL, 'NOT_ESTIMABLE', '138', 'N_TIES=1 (TAM); folds into TAM''s own figure.'),
('DIB', 'MNT', 'DIB', 'DAM_LOAD_ADJUSTED', '138', NULL),
('DIB', 'SRB', 'DIB', 'DAM_LOAD_ADJUSTED', '138', NULL),
('DOWGEN', 'DOW', 'DOWGEN', 'EXACT_SWITCHING', '138', NULL),
('DUP1_V', 'STONERSY', 'STONERSY', 'ENTANGLED_GROUP', '138', 'Entangled group ''STONERSY'': shares real neighbour(s) with DUPV1; group figure only, not individually attributable.'),
('DUP2_V', 'INV_TAP', 'DUP2_V', 'EXACT_SWITCHING', '138', NULL),
('DUPV1', 'STONERSY', 'STONERSY', 'ENTANGLED_GROUP', '138', 'Entangled group ''STONERSY'': shares real neighbour(s) with DUP1_V; group figure only, not individually attributable.'),
('EQUISTAR', 'LON_HILL', 'EQUISTAR', 'DAM_LOAD_ADJUSTED', '138', 'N_TIES=3 > N_REAL_NEIGHBORS=2: parallel ties to the same neighbour(s), deduplicated here.'),
('EQUISTAR', 'MCKENZIE', 'EQUISTAR', 'DAM_LOAD_ADJUSTED', '138', 'N_TIES=3 > N_REAL_NEIGHBORS=2: parallel ties to the same neighbour(s), deduplicated here.'),
('EXN', 'BT', 'EXN', 'DAM_LOAD_ADJUSTED', '138', NULL),
('EXN', 'DKR', 'EXN', 'DAM_LOAD_ADJUSTED', '138', NULL),
('EXN', 'LH', 'EXN', 'DAM_LOAD_ADJUSTED', '138', NULL),
('FORMOSA', 'JOSLIN', 'FORMOSA', 'DAM_LOAD_ADJUSTED', '138', NULL),
('FORMOSA', 'LOLITA', 'FORMOSA', 'DAM_LOAD_ADJUSTED', '138', NULL),
('INGLCOSW', NULL, NULL, 'NOT_ESTIMABLE', '138', 'N_TIES=2 (I_DUPP1, OXY_INGL); exits via TWO boundary PUNs at once (I_DUPSW group and OXY_INGL), split across two group figures, not folded into one.'),
('I_DUPP1', 'I_DUPSW', 'I_DUPSW', 'ENTANGLED_GROUP', '138', 'Entangled group ''I_DUPSW'': shares real neighbour(s) with LGE; group figure only, not individually attributable.'),
('LBM3', NULL, NULL, 'NOT_ESTIMABLE', '138', 'N_TIES=1 (PSA); folds into PSA''s LY-group combined figure.'),
('LEVEE', 'OYS', 'LEVEE', 'EXACT_SWITCHING', '138', NULL),
('LGE', 'I_DUPSW', 'I_DUPSW', 'ENTANGLED_GROUP', '138', 'Entangled group ''I_DUPSW'': shares real neighbour(s) with I_DUPP1; group figure only, not individually attributable.'),
('LHM', 'LY', 'LY', 'ENTANGLED_GROUP', '138', 'Entangled group ''LY'': shares real neighbour(s) with PSA; group figure only, not individually attributable.'),
('LKVPD', 'LKVEW_RC', 'LKVPD', 'DAM_LOAD_ADJUSTED', '138', NULL),
('LKVPD', 'LKVTP_RC', 'LKVPD', 'DAM_LOAD_ADJUSTED', '138', NULL),
('LKVPD', 'LLTSW', 'LKVPD', 'DAM_LOAD_ADJUSTED', '138', NULL),
('LKVPD', 'PLSTH', 'LKVPD', 'DAM_LOAD_ADJUSTED', '138', NULL),
('LKVPD', 'TIMBR', 'LKVPD', 'DAM_LOAD_ADJUSTED', '138', NULL),
('LYD', 'DPW', 'DPW', 'ENTANGLED_GROUP', '138', 'Entangled group ''DPW'': shares real neighbour(s) with CHE; group figure only, not individually attributable.'),
('LYD', 'GBY', 'DPW', 'ENTANGLED_GROUP', '138', 'Entangled group ''DPW'': shares real neighbour(s) with CHE; group figure only, not individually attributable.'),
('MATKM', 'SUNSW', 'MATKM', 'DAM_LOAD_ADJUSTED', '138', 'N_TIES=2 > N_REAL_NEIGHBORS=1: parallel ties to the same neighbour(s), deduplicated here.'),
('MIN', 'BNT', 'MIN', 'DAM_LOAD_ADJUSTED', '69', NULL),
('MPPOI', 'KEYSB', 'MPPOI', 'DAM_LOAD_ADJUSTED', '138', NULL),
('MPPOI', 'WLVSW', 'MPPOI', 'DAM_LOAD_ADJUSTED', '138', NULL),
('MSN', 'HUD', 'HUD', 'ENTANGLED_GROUP', '138', 'Entangled group ''HUD'': shares real neighbour(s) with AK; group figure only, not individually attributable.'),
('MSN', 'PET', 'HUD', 'ENTANGLED_GROUP', '138', 'Entangled group ''HUD'': shares real neighbour(s) with AK; group figure only, not individually attributable.'),
('NCARBIDE', 'CANGREJO', 'NCARBIDE', 'DAM_LOAD_ADJUSTED', '69;138', 'N_TIES=8 > N_REAL_NEIGHBORS=6: parallel ties to the same neighbour(s), deduplicated here.'),
('NCARBIDE', 'GREENLK', 'NCARBIDE', 'DAM_LOAD_ADJUSTED', '69;138', 'N_TIES=8 > N_REAL_NEIGHBORS=6: parallel ties to the same neighbour(s), deduplicated here.'),
('NCARBIDE', 'PV_TAP', 'NCARBIDE', 'DAM_LOAD_ADJUSTED', '69;138', 'N_TIES=8 > N_REAL_NEIGHBORS=6: parallel ties to the same neighbour(s), deduplicated here.'),
('NCARBIDE', 'SANDCRAB', 'NCARBIDE', 'DAM_LOAD_ADJUSTED', '69;138', 'N_TIES=8 > N_REAL_NEIGHBORS=6: parallel ties to the same neighbour(s), deduplicated here.'),
('NCARBIDE', 'SEADRFTC', 'NCARBIDE', 'DAM_LOAD_ADJUSTED', '69;138', 'N_TIES=8 > N_REAL_NEIGHBORS=6: parallel ties to the same neighbour(s), deduplicated here.'),
('NCARBIDE', 'SEADRIFT', 'NCARBIDE', 'DAM_LOAD_ADJUSTED', '69;138', 'N_TIES=8 > N_REAL_NEIGHBORS=6: parallel ties to the same neighbour(s), deduplicated here.'),
('OXY_CC', NULL, NULL, 'NOT_ESTIMABLE', '138', 'N_TIES=1 (EQUISTAR); folds into EQUISTAR''s own figure (own SCED gross ~6.4 MW already inside EQUISTAR''s I_PUN).'),
('OXY_INGL', 'ALIQUING', 'OXY_INGL', 'DAM_LOAD_ADJUSTED', '138', 'N_TIES=2 > N_REAL_NEIGHBORS=1: parallel ties to the same neighbour(s), deduplicated here.'),
('P66SUB12', NULL, NULL, 'NOT_ESTIMABLE', '138', 'N_TIES=1 (COPSUB10); part of COPSUB8->CPCSUB9->COPSUB10->P66SUB12 isolated chain, exits via SCLPCOGN (PHILLPS2 group).'),
('P66SUB6', NULL, NULL, 'NOT_ESTIMABLE', '69', 'N_TIES=2 (P66_3, SCLPCOGN); exits via P66_3 (DAM_LOAD_ADJUSTED) or SCLPCOGN (PHILLPS2 group), not separately attributable.'),
('P66_3', 'P66SUB2', 'P66_3', 'DAM_LOAD_ADJUSTED', '69', 'N_TIES=2 > N_REAL_NEIGHBORS=1: parallel ties to the same neighbour(s), deduplicated here.'),
('PHILLPS5', 'OLDOCEAN', 'PHILLPS2', 'ENTANGLED_GROUP', '69', 'Entangled group ''PHILLPS2'': shares real neighbour(s) with SCLPCOGN; group figure only, not individually attributable.'),
('PHILLPS5', 'PHILLPS2', 'PHILLPS2', 'ENTANGLED_GROUP', '69', 'Entangled group ''PHILLPS2'': shares real neighbour(s) with SCLPCOGN; group figure only, not individually attributable.'),
('PL', 'BER', 'PL', 'DAM_LOAD_ADJUSTED', '138', 'N_TIES=3 > N_REAL_NEIGHBORS=2: parallel ties to the same neighbour(s), deduplicated here.'),
('PL', 'CO', 'PL', 'DAM_LOAD_ADJUSTED', '138', 'N_TIES=3 > N_REAL_NEIGHBORS=2: parallel ties to the same neighbour(s), deduplicated here.'),
('PNPI', 'WAP', 'PNPI', 'DAM_LOAD_ADJUSTED', '138', NULL),
('PR', 'PRS', 'PR', 'EXACT_SWITCHING', '69', NULL),
('PSA', 'BCV', 'LY', 'ENTANGLED_GROUP', '138', 'Entangled group ''LY'': shares real neighbour(s) with LHM; group figure only, not individually attributable.'),
('PSA', 'HL', 'LY', 'ENTANGLED_GROUP', '138', 'Entangled group ''LY'': shares real neighbour(s) with LHM; group figure only, not individually attributable.'),
('PSA', 'LY', 'LY', 'ENTANGLED_GROUP', '138', 'Entangled group ''LY'': shares real neighbour(s) with LHM; group figure only, not individually attributable.'),
('PSA', 'MTS', 'LY', 'ENTANGLED_GROUP', '138', 'Entangled group ''LY'': shares real neighbour(s) with LHM; group figure only, not individually attributable.'),
('SCLPCOGN', 'FM524', 'PHILLPS2', 'ENTANGLED_GROUP', '69;138', 'Entangled group ''PHILLPS2'': shares real neighbour(s) with PHILLPS5; group figure only, not individually attributable.'),
('SCLPCOGN', 'LINVILLE', 'PHILLPS2', 'ENTANGLED_GROUP', '69;138', 'Entangled group ''PHILLPS2'': shares real neighbour(s) with PHILLPS5; group figure only, not individually attributable.'),
('SCLPCOGN', 'PHILLPS2', 'PHILLPS2', 'ENTANGLED_GROUP', '69;138', 'Entangled group ''PHILLPS2'': shares real neighbour(s) with PHILLPS5; group figure only, not individually attributable.'),
('SCLPCOGN', 'WCOLMAIN', 'PHILLPS2', 'ENTANGLED_GROUP', '69;138', 'Entangled group ''PHILLPS2'': shares real neighbour(s) with PHILLPS5; group figure only, not individually attributable.'),
('SDSES', 'SNDSW', 'SDSES', 'DAM_LOAD_ADJUSTED', '138', NULL),
('SL', 'AZ', 'SL', 'DAM_LOAD_ADJUSTED', '12;34;138', 'N_TIES=4 > N_REAL_NEIGHBORS=2: parallel ties to the same neighbour(s), deduplicated here.'),
('SL', 'BOG', 'SL', 'DAM_LOAD_ADJUSTED', '12;34;138', 'N_TIES=4 > N_REAL_NEIGHBORS=2: parallel ties to the same neighbour(s), deduplicated here.'),
('SPPKM', NULL, NULL, 'NOT_ESTIMABLE', '138', 'N_TIES=1 (MATKM); folds into MATKM''s own figure.'),
('TAM', 'ATKINS', 'TAM', 'DAM_LOAD_ADJUSTED', '138', 'N_TIES=3 > N_REAL_NEIGHBORS=2: parallel ties to the same neighbour(s), deduplicated here.'),
('TAM', 'ENTERPR', 'TAM', 'DAM_LOAD_ADJUSTED', '138', 'N_TIES=3 > N_REAL_NEIGHBORS=2: parallel ties to the same neighbour(s), deduplicated here.'),
('TC', 'BG', 'TC', 'DAM_LOAD_ADJUSTED', '138', NULL),
('TC', 'GN', 'TC', 'DAM_LOAD_ADJUSTED', '138', NULL),
('UCC_COGN', 'APACHE', 'UCC_COGN', 'EXACT_SWITCHING', '138', NULL),
('VISTRON', 'BLCBAYU4', 'VISTRON', 'DAM_LOAD_ADJUSTED', '138', 'N_TIES=2 > N_REAL_NEIGHBORS=1: parallel ties to the same neighbour(s), deduplicated here.');

-- ===========================================================================
-- Verification
-- ===========================================================================
-- Row/PUN counts should read 90 total rows, 56 distinct PUNSTATION, 72
-- distinct non-null NEIGHBORSTATION, and method-tag counts 8/24/12/12:
--
-- SELECT COUNT(*) AS N_ROWS, COUNT(DISTINCT PUNSTATION) AS N_PUNS,
--        COUNT(DISTINCT NEIGHBORSTATION) AS N_NEIGHBORS
-- FROM AWDEV.ERCOTRT.ERCOTPUNTIEMAP;
--
-- SELECT METHODTAG, COUNT(DISTINCT PUNSTATION) AS N_PUNS, COUNT(*) AS N_ROWS
-- FROM AWDEV.ERCOTRT.ERCOTPUNTIEMAP GROUP BY METHODTAG ORDER BY 1;
--
-- No neighbour should ever appear twice for the same PUN (would double-count
-- N_S in the loader):
--
-- SELECT PUNSTATION, NEIGHBORSTATION, COUNT(*) FROM AWDEV.ERCOTRT.ERCOTPUNTIEMAP
-- WHERE NEIGHBORSTATION IS NOT NULL
-- GROUP BY PUNSTATION, NEIGHBORSTATION HAVING COUNT(*) > 1;
