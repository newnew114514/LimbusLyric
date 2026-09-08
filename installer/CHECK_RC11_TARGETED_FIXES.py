from __future__ import annotations
import ast, hashlib, sys
from pathlib import Path

# Accuracy-first final hybrid: software-2 remains QQ UIA/stable-state authority. Reviewed
# deviations may improve observation/QRC latency, stale-control recovery, and arbitrate a
# source-affine healthy GSMTC session against an obviously wrong UIA duration. Geometry never
# drives lyric time, and the GSMTC guard is inactive when the system timeline is untrusted.
SOFTWARE2_LOCKED = {'ControlPanel._on_auto_lyric_result': '2cb21c35ee0fc7ac5f758007ecf722addb955bffa6d07da64128e6296e9127b6',
 'MediaSessionSync._qq_consume_lyric_click_candidate': '17ddb988232f32a3aba9a6ff6be1f97c23883e33c36a16815d6299da7bba0c1a',
 'MediaSessionSync._qq_expected_from_cursor': 'c050321e3bcd21cbc6bc844370ed663f7e54482dc5179e067841e148560a6976',
 'MediaSessionSync._qq_left_mouse_down': 'dce6c4c8bc0ffa07c239392247063dec06d3401ed09311a2f624764e96d9270b',
 'MediaSessionSync._qq_note_clock_sample': 'e86e2bf2a13a635d8adca1e02f54c9c5d8eef6452bf7f7fd0c28db5b56603bbd',
 'MediaSessionSync._qq_note_hover_safe_clock': '6f478f9421fdce1688144ece31d115c3c860cd48c27b71f2f2d5cc90964d27a2',
 'MediaSessionSync._qq_pending_mouse_down': '9a8ee0afae5b4cfc6f88061f94c5d0992a1701dfede493768520125fb65df257',
 'MediaSessionSync._qq_seek_phase_carry': '26f63d515b8bffbfb1ef101ac7bd97557cd7fe36b7e857cf32b77584ae9047b2',
 'MediaSessionSync._qq_select_public_clock': 'ff05212ac76f71caaf66f60076566e5edeef3e2f65f3fad64af16e3f217664f9',
 'QQMusicUiAdapter.__init__': '2729bfcf4a5ff8e9e6b28e8d980f5a400c9387d4ef1e9c70440f2e1b3cffada3',
 'QQMusicUiAdapter._best_pair': '2f8bfb3d8b60d08e4a01e5843cc79bbb2219d03dee5095152d65ce0e8817fb89',
 'QQMusicUiAdapter._center': 'f811794436de07ca60fb3c6133415d556d4ab319bc70d91b78b7a13eb1870a1b',
 'QQMusicUiAdapter._duration_ready': '78e342f4eb0e9d598699a85eb89591a57d2ea57e1a22dfd1fe4ad2aaeb42ed51',
 'QQMusicUiAdapter._interaction_hint': '6917b6e58fec02c1b57415cac04cb6794975cdb35cdcc764a0399ad921c0db25',
 'QQMusicUiAdapter._load_cache': '776d0be3379fb5af721e32670bc663b2aab812af50bdef1f01c8e0f8658e6884',
 'QQMusicUiAdapter._make_result': '18cea90aebf0c95aa66efcd4ad5d8e575c5d0aa637acd4d740c2af7e20a95789',
 'QQMusicUiAdapter._pair_geometry_usable': '6dab1a137dbcda11790a5f3b006dcecf88787f7de8879a8bfffa22a26e3bf0ed',
 'QQMusicUiAdapter._pair_key': 'a338248ddbfd76526897bca067e46d9b006d1e08ad298f04e6b78913df7309f3',
 'QQMusicUiAdapter._pair_signature': '5fcba6c596fbeb61916704141426f2d877a3afcabc1e39b9cad6ada344761af0',
 'QQMusicUiAdapter._pair_signature_coherent': '9ffba5272987c3c706df02d1bba7db761435f811c2f8e1896e36f43255898837',
 'QQMusicUiAdapter._progress_band_from_pair': '5d798fd512194cfe15f45ee3f0f0335d4696edcbf8f2019ef1a9e38c82619fc0',
 'QQMusicUiAdapter._read_live_time_control': 'be2b67a3983100a489598061c6bedfa375052c6abb1771fa9ff56d8b7c1ddc79',
 'QQMusicUiAdapter._read_near': '387a08d41c1292ba92d010848f956bcc2b28121f9f88b125bd98a3af592ff1bf',
 'QQMusicUiAdapter._rect_usable': '25e8c369ac2e9bcb9aa61b3d81ce1742c27433f16bf4cfa74c48260c58f9c435',
 'QQMusicUiAdapter._remember_geometry': '31174290f71aba84ef45f547c866188350db9fc919e8620e8aa37e71ecfb9f3c',
 'QQMusicUiAdapter._save_cache': '61b59c23f2e7b9da98cd18629f4e3927d84fd2c45cfb83d6cd4380ed9d1c61a1',
 'QQMusicUiAdapter._single_time_from_chain': 'd26c4eaacb54ae38b1d9200b775e9ac46457c6e98612a4cae9e067909268e9dc',
 'QQMusicUiAdapter._try_broad_probe': 'b9ab02753ef514d777bdc25588113e0740a14e7a7fa413b085cc1e801e89269c',
 'QQMusicUiAdapter._try_live_controls': '9fdc2d9e5e4e63956a6ebfc72c6ddfe725a8e95ad3a5d731d0ca425c7323f4ec',
 'QQMusicUiAdapter._try_saved_geometry': 'eed599fdc19d3f0499d5c1169e86735720af7794e8fef729c7a511e2560dae5a',
 'QQMusicUiAdapter.accept_discovered_pair': 'b6886f8597d7f1387a32cc2c9180307261c47769fffeac55fb68fed81d5ba474',
 'QQMusicUiAdapter.is_qq': 'e93d1d87d976b0c7830868e0d6b803e357a5d137a50a260ac7fe008d660250dd',
 'QQMusicUiAdapter.poll': '52b8584ac33cf686e003b8fe668819c146eff11f0b9df51071851cccc388d650',
 'QQMusicUiAdapter.reset_for_track': '04c3987506574f04df7e96b734f19de5e55c1b09687b3d4b3ea1d5ed1d310ecd'}

# RC UI HYGIENE 20260816: the two status-producing functions above are re-locked after
# wording-only user-facing changes; CHECK_RC_UI_HYGIENE_LOG5_REPLAY covers those exact labels.

QQ_TEXT_BOUNDARY_REVIEWED = {
 'MediaSessionSync._merge_uia_position': '35269b1b816d2dcfa379e419ea5731b607219147ec86b58f68a062963505b86e',
 'MediaSessionSync._qq_phase_edge_correction': 'f901325f871e827abdd2e01e0e9c0f306e01727f09a9cfae43f058b02a2b1f37',
 'MediaSessionSync._qq_reset_clock_authority': '5205e5c1dbfe972269d683b9320aac8abf4a8f9e14050dd1281230d70ecf8892',
}

# 2026-08-17: MediaSessionSync.__init__ lock includes one observational slow-call timestamp field only.
# 2026-08-19 H8/H8F1 re-locks __init__ after async click verification plus a bounded KuGou deferred-hook queue; QQ software-2 clock/seek selectors remain unchanged.
# 2026-08-17 precision ladder/QQ-background review: six hashes below intentionally track
# retrieval-mode propagation plus a display-only hidden-window clock branch; provider authority remains unchanged.
# V12 intentionally re-locks LyricSearchEngine.search after one retrieval-only change: a confirmed
# instrumental primary payload skips foreign quality enhancement. No clock/seek/provider authority changed.
# V19 gate refresh: the prior targeted hashes were stale relative to the already-passing V18 tree.
# Search/MediaSessionSync/request/start/monitor hashes below are identical V18→V19; only
# _on_auto_lyric_result changes in V19 to clear stale presentation duration, without clock authority.
# V23/R2.4 re-lock: bind_track now enforces startup-existing no-synthetic-zero across every player and exposes only existing/display-only rescue lanes.
# V26 re-locks four outer lifecycle methods after player/identity/Range epoch ownership closure.
# H25 re-locks MediaSessionSync._poll_loop/bind_track and ControlPanel._start_auto_search_job after reviewed NetEase Win10-safe visual-clock integration and KuGou marquee-credibility enrichment only; QQ software-2 clock/seek selectors remain unchanged.
# V29 re-locks three outer lifecycle methods after KuGou-only play-instance bookkeeping was reviewed:
# 2026-08-18 H6 re-locks __init__/bind/_poll_loop after QQ-only centralized background loop-transport state.
# 2026-08-20 H10F1 re-locks _poll_loop/start/fetch_and_set/_monitor_track_change after player-presence fetch guards; formal QQ/KG clock/seek selectors remain unchanged.
# 2026-08-21 H10F4 re-locks only _qq_commit_seek_if_ready and _qq_note_unarmed_far_seek: a rail commit now records its same-gesture geometry hint, and only a geometry/UIA-conflicted commit may recover through a strict three-sample advancing trend while preserving the 12.5s host stale-stream veto.
# 2026-08-20 H10F2 re-locks __init__/start after KuGou inactive-hook capture gating and
# _qq_rebase_auto_local_from_coherent_uia after startup-attach single-sample display seed rejection.
# Dedicated H10F2 replay proves auto-track fast seed remains display-only and KuGou active gestures remain enabled.
# H83 CODEX SAFE SALVAGE re-locks the three shared auto-lyric entry methods after NetEase-only track-ID cache/search/result guards; QQ/KuGou clock and seek selectors are unchanged.
# H84 re-locks only MediaSessionSync._poll_loop after adding player-epoch/process late-publication guards; WinRT request cadence and QQ/KuGou seek/clock selectors remain unchanged.
# 2026-08-18 H7 re-locks the same three outer methods after KuGou-only pause authority closure:
# explicit playback pause/resume is applied on MediaSync, paused new-track binds no longer invent playing,
# and the public status follows the public rail-local clock. QQ software-2 selectors remain unchanged.
# Formal software-2 clock/seek selectors remain separately locked below; the new lane is display/transport-only.
# Event callbacks publish only transport serial evidence; they do not become position/seek/provider authority.
# __init__ adds transport-generation state, reset/bind only clear pending end-continuation proof.
# QQ Software-2 authority/seek methods remain exact and no provider identity authority is widened.
# The reviewed changes retire cross-player duration/Range evidence, stamp identity ownership, and keep
# pre-bind KuGou Range duration out of provider filtering. QQ Software-2 seek/clock methods remain exact.
# V24 re-locks MediaSessionSync._qq_queue_seek after a baseline-reviewed edge fix: a released gesture may
# accept high-confidence qq-time-pair-validated evidence only when it is far from the stale old clock and
# materially closer to the gesture intent. Rail geometry remains non-authoritative and stale-control guards remain.
# 2026-09-08 R2.1 re-locks ControlPanel._start_auto_search_job after reviewed first-safe-main display, search-only KuGou artist enrichment, and rapid-switch cancellation debounce; transport/seek authority remains player-owned.
# 2026-09-08 R2 re-locks QQ adapter duration-proof/search and merge boundaries after reviewed
# player-owned advancing-time duration proof, QQ 5xx circuit-breaker wiring, and provisional cross-provider
# precise-version quarantine. Seek geometry authority remains unchanged and dedicated QQ replays cover behavior.
# 2026-09-08 S2 audit follow-up: source-lock fallback was made explicit again so the historical
# H95F10 replay can inspect provider_locked behavior while core provider ordering remains preferred.
# 2026-09-08 S2 re-locks LyricSearchEngine.search after provider dispatch was moved behind the
# provider-neutral LyricQuery/ProviderRegistry contract with an in-function legacy-direct fail-safe.
# Dedicated H95F10F1/H41/H81/H95F10F6/H95F10F8 gates cover search-chain and identity equivalence.
# 2026-09-07 H95F10 re-locks only the bilingual retrieval boundary: same-provider main/translation
# pair selection, bilingual cache-key separation, and mode/manual propagation. QQ/KuGou clock/seek
# selectors remain separately locked and unchanged.
# V14/V15 re-locks only reviewed lyric-pipeline functions: payload provenance/caching, source-switch
# lyric-only requeue, old-loaded suppression, and V20 pending-transaction identity closure;
# its prior hash in this gate was stale. Media clock/seek/player authority remains outside this patch.
SAFE_FASTSTART_PATCH = {'AsyncPlayerUiPositionReader.__init__': '24acbef433b649ae4467c4544fb37b412a2649238b9076b8f961baa16451632c',
 'AsyncPlayerUiPositionReader._guard_qq_duration_mismatch_result': '046407a930c1ebf2cd0e98fa5c366e23192375808a304907618572f1787b7151',
 'AsyncPlayerUiPositionReader._kick_accessibility': '2bde573e0212b55530f9ac2565fdd137dac5d7fa62b74568992b925cad5e1b82',
 'AsyncPlayerUiPositionReader._start_accessibility_wake': 'b89c9fafd5a977e6c0281fa90c222b4c0063ce639ac86a62cc97e3b34d0f1f02',
 'AsyncPlayerUiPositionReader._worker_main': 'fa0fc331d16359d1123b17105243c41ad6358e1fce83a880c35223d3fcf2b77b',
 'AsyncPlayerUiPositionReader._guard_kugou_numeric_causal_result': 'd0f7e8abcab7c93673e2c86f9ddb045fb55de33b4dacd33c9c92406c8d2f6bdf',
 'AsyncPlayerUiPositionReader.poll': '9a06b15f839a3be8cbfbbf2fc08dd02f67997966bad2313ce390a6cc4018e994',
 'AsyncPlayerUiPositionReader.request_qq_live_reacquire': '22bcd444e8402936cd5ec46dd4bdad53fe276b0aa83538c9ed3afc5d640f9d66',
 'AsyncPlayerUiPositionReader.reset_qq_track_soft': '5a52951fc44f6084f6ba85a488e586e3901fed64baa121c749a6435316666b6b',
 'AsyncPlayerUiPositionReader.set_qq_gsmtc_identity_guard': '0e88eb23a73da916c79a4c55c26517d0d320c82af6131f776a684737db5acc55',
 'AsyncPlayerUiPositionReader.set_qq_gesture_candidate_quarantine': '2ac07e68bdc301ed160e009e99b5d57174311d7a18375002f32ebd60225b185e',
 'LyricSearchEngine.search_qq': 'f395daaf6a45f2806b676add93f66a04af42ebe6c9d2b39c71ba3dd878770f63',
 'LyricSearchEngine.search': '68e963984357b4924842f1c8782defd798a0ddf438d618c4e4b266f7ee844362',
 'MediaSessionSync.__init__': '1ead6c3168cf744391f4cdd6e9bc2ed5ff992e8b2631931472e537d45cbf2688',
 'MediaSessionSync._poll_loop': 'ea86bb9a63bc9bcca4fedcd974b5e33da0437895cffce14ada0a25be29e145c4',
 'MediaSessionSync._qq_commit_seek_if_ready': 'efc86cf0c0b8eeee0dca4c1e0ee0bc579cd2002dac9eec099929a500618e8a57',
 'MediaSessionSync._qq_nonrail_seek_click_plausible': '0f57109012dfbf42c7261e714e739aa22fc5e720ae78d5bb0e9a3f8e65ee7a67',
 'MediaSessionSync._qq_note_unarmed_far_seek': '114f282be34f3d496362cdd91f1c7c1e14aae050d48e1fad1197fcb0a526f3ea',
 'MediaSessionSync._qq_poll_pointer_gesture': 'e505edbc66f212dec785c4ef984f54eb20ca1acdd39f51747811ea505928eec8',
 'MediaSessionSync._qq_queue_seek': 'fa17d281b3ffd10bfa54fa458522470381563ea11bd5a91ec5d19b0d80542cc7',
 'MediaSessionSync._qq_rebase_auto_local_from_coherent_uia': 'f5672f42b3fb7d1555b9e286481be33dd84002c6df6746130dedd51410fd4049',
 'MediaSessionSync._guard_auto_local_handoff': '0580a5ddac6a67c9ca7f91cf059118f92e80c3cfba5c091275ad7ea0e37dab17',
 'MediaSessionSync._auto_local_position': '62dfb103487dc7e3936a366d4f519d3b18e68cbed048621041df628001a1eb0e',
 'MediaSessionSync._reset_auto_local_clock': 'c3594e28c10c81f99267f401e971a3e8b9eeb741b7ca55ede0e5584021379619',
 'MediaSessionSync._arm_auto_local_unknown_play_carry': '407e84f78499c8658a5f4f5b9595796b9ddc351b4e7b64ade0317f40c58f231d',
 'MediaSessionSync._qq_try_prelock_rail_validated_anchor': '3c2977f15b52e6d7824f0bd962f46e6247a98a99f36a1eec6c9d7261c797906f',
 'MediaSessionSync._qq_update_gsmtc_identity_guard': 'b83e90112aadd15d33baa205beda8824eac90118fb1f4b8778defb7f87322b5a',
 'MediaSessionSync._qq_direct_gsmtc_witness': '85247581222af7ec0d1a218cbc60949a89a9eda0567e6a136d9c7a8f7c6ee10a',
 'MediaSessionSync._qq_apply_direct_gsmtc_seek_authority': '03ed2cd5dc487136c4ef7f081c1518dd904e2223b3dbbd1f12847613d85e1068',
 'MediaSessionSync._qq_direct_public_clock_override': '9ca681e17bff4a2aef0e6133f969f896c6a54b16f2270d8561a9686d3af8a2e7',
 'MediaSessionSync._qq_direct_gsmtc_veto_allowed_after_rail': 'ba2b949adf2b41bb6433915c5c64d250ab0dd8088c74d987af482aa887f0e333',
 'MediaSessionSync._qq_seed_phase_calibration_after_initial_lock': 'f8030805691c63e70b0b67c68f4dff3c6b1ad4557c1759f5ccd92cae535582b7',
 'MediaSessionSync._reset_provider_sync_state': '752413c73241d929ed33e9319ca9e5929f783a457db5d44b4fe0c0013a5dbb31',
 'MediaSessionSync.bind_track': '2aad0ee42f6bc5e8dc21a418f754e53dd9d696f5bba75b2389fe58c8fca2b5a8',
 'MediaSessionSync.start': '72fc8a8762430c81b1d0fa3ecd5994aeaaf06bc9b87d25350b3c8549e31a6fed',
 'PlayerUiPositionReader.invalidate_qq_live_controls': '0b55bc1fbd3ffe84c37de26ea0aa81192b3c4cbd88c79c19cd148305128d605b',
 # 2026-09-08 R2.4: first-attach lifecycle is consumed by confirmed track bind, not provider-result branches; formal player authority unchanged.
 # 2026-08-18 V29 maintenance re-lock: _start_auto_search_job only persists an already-validated cache_put row; QQ duration/version authority branches are byte-identical.
 'ControlPanel._request_auto_track': 'c393efaae3d37ee7507992b9ac12bfc1990a9c62efe881968455fc1c311631a4',
 'ControlPanel._start_auto_search_job': '32b27be278c1dc908f6518f6030c22699cc1b5b9f7cd133077fae88639cce5bc',
 'ControlPanel._resolve_qq_auto_track_duration_after_bind': '7a2b8fea3f659d9b135f9828c949428b2357949e99f541ef9e296dcc1b85a886',
 'LyricFetcher.fetch_and_set': '4a98199166266e55b659513c3573475c4d9f9b66ad472f7aafad68a030829d7c',
 'ControlPanel._monitor_track_change': 'acb2e70bd9cea22394ae467d118856bda8fa2dd989bd98877ea410311d37328e',
 'ControlPanel._refetch_loaded_track_for_mode_switch': '5b433f9318887544add4e82bb72430155d0df354468197c679d4c8a40cc8570b',
 'LyricFetcher.get_qq_ui_duration_hint': '46148957431c6e08226c83783b7eaeed404714143b90028f62b136a6039168c9',
 'ControlPanel._restore_qq_suspended_loaded_track': '37d13b6927f1ee1061c3280b1637282357803085c818c99b8b588d49d54d5cd9',
 'ControlPanel._on_qq_auto_lyric_transaction_result': '5950bdf6da989a1204004cdf2d1ebc3daf066dff07be8c48b5ff950948d39fb1'}

if len(sys.argv) != 2:
    print('usage: CHECK_RC11_TARGETED_FIXES.py <main.py>')
    raise SystemExit(2)
path=Path(sys.argv[1]); source=path.read_text(encoding='utf-8')

def collect(text):
    tree=ast.parse(text, filename=str(path)); lines=text.splitlines(); out={}
    def walk(body,prefix=''):
        for n in body:
            if isinstance(n, ast.ClassDef):
                q=f'{prefix}.{n.name}' if prefix else n.name; walk(n.body,q)
            elif isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
                q=f'{prefix}.{n.name}' if prefix else n.name
                out[q]='\n'.join(lines[n.lineno-1:n.end_lineno]).rstrip()+'\n'
    walk(tree.body); return out

funcs=collect(source); fail=[]
def check(mapping,label):
    for q,expected in mapping.items():
        if q not in funcs:
            fail.append(f'{label} {q}: missing'); continue
        actual=hashlib.sha256(funcs[q].encode()).hexdigest()
        if actual != expected:
            fail.append(f'{label} {q}: hash mismatch')
check(SOFTWARE2_LOCKED,'software-2 authority lock')
check(QQ_TEXT_BOUNDARY_REVIEWED,'reviewed QQ text-boundary authority lock')
check(SAFE_FASTSTART_PATCH,'reviewed accuracy/recovery patch lock')

for token in (
    'QQ_STARTUP_CALIBRATION_', 'QQ_GESTURE_RELEASE_SETTLE_MS',
    'QQ_GESTURE_TARGET_TOLERANCE_', 'QQ_LYRIC_TEXT_PROBE_DEFER_MS',
    'QQ_POST_SEEK_QUICK_REPHASE_', 'QQ_RAIL_VISUAL_TTL_MS',
    '_qq_startup_calibration_', '_qq_deferred_lyric_probe',
    '_qq_post_seek_quick_rephase', '_write_qq_stability_summary',
    'QQ_INTERACTION_ANCHOR_', '_qq_interaction_anchor_stream_step',
    'QQ交互首锚确认', 'QQ冷启动进度条临时时钟',
    'QQ开局可信样本临时时钟', 'qq-rail-provisional-preview',
    'QQ_PHASE_EDGE_FORWARD_CATCHUP_', 'baseline_eligible',
):
    if token in source: fail.append('accuracy regression token present: '+token)
for token in (
    'QQ冷启动歌词点击轻探测', 'QQ启动加速扫描',
    'expected_release_age', 'race=1', 'for wave in (profiles[:2], profiles[2:])',
    'reset_qq_track_soft', 'QQ切歌复用活控件软重置', '_wake_last_hwnds', '_qq_track_epoch',
    'qq-rail-visual-wait-uia', 'request_qq_live_reacquire',
    'invalidate_qq_live_controls', 'QQ Seek旧时间控件疑似冻结，触发重抓',
    'QQ_GSMTC_IDENTITY_GUARD_ENABLED', 'set_qq_gsmtc_identity_guard',
    'qq-gsmtc-veto-uia-duration', 'QQ健康GSMTC否决错误UIA时长', 'QQ健康GSMTC Seek二样本确认',
    'QQ切歌首锚前临时时钟可信流对齐', 'QQ Seek后迟到旧流隔离',
    'QQ_POST_RAIL_UNARMED_STALE_WINDOW_MS', 'QQ_AUTO_LOCAL_REBASE_MIN_DRIFT_MS',
    'set_qq_gesture_candidate_quarantine', 'qq-gesture-candidate-quarantine',
    'QQ歌词版本时长严格匹配', 'QQ歌词版本时长拒绝',
    'QQ自动歌词搜索时长证据', 'QQ自动歌词版本时长拒绝',
    'QQ歌词搜索时长证据', 'QQ手动歌词版本时长拒绝',
    'QQ自动歌词失败事务解锁', 'QQ失败切歌回到旧曲恢复弹幕',
    'get_qq_ui_duration_hint', '_on_qq_auto_lyric_transaction_result',
    'QQ_DIRECT_GSMTC_POSITION_VETO_MIN_DELTA_MS', '_qq_direct_gsmtc_witness',
    'QQ独立GSMTC否决错误UIA位置', 'QQ独立GSMTC Seek接管', 'gsmtc-qq-direct-witness',
    '跨平台完整歌词借用命中', '三平台完整歌词均未命中',
    'QQ Rail交接旧GSMTC证据暂缓否决', 'QQ首锚可信流直接授予相位校准资格',
    'QQ_DIRECT_GSMTC_RAIL_HANDOFF_SUPPRESS_MS',
    'QQ自动切歌前旧流时长不作为新曲身份', 'QQ自动切歌新曲时长证据',
    'QQ_AUTO_TRACK_DURATION_REFRESH_WAIT_MS', '_resolve_qq_auto_track_duration_after_bind',
    '_qq_transport_duration_evidence', 'QQ自动歌词时长冲突以GSMTC为准', 'QQ手动歌词时长冲突以GSMTC为准',
    'QQ_AUTO_LOCAL_FAST_SEED_MAX_AGE_MS', 'QQ首锚前快速临时时钟采样',
    'AUTO_TRACK_UNKNOWN_PLAY_CARRY_MAX_MS', '_arm_auto_local_unknown_play_carry',
    '新曲临时时钟沿用最近播放态', 'paused-stopped=veto',
    'qq-auto-track-wait-display-seed', 'authority=display-only',
    'QQ_STARTUP_PROVISIONAL_HANDOFF_MAX_DRIFT_MS', 'QQ首曲恢复旧Text拒绝接管',
    '_qq_try_prelock_rail_validated_anchor', 'QQ首锚前Rail可信UIA直锚', 'geometry_authority=0',
    '_guard_kugou_numeric_causal_result', 'kugou-numeric-causal-quarantine',
    '酷狗数值内存仅连续证明，暂不授予歌词时钟', '酷狗数值内存假时钟因果否决',
    '酷狗数值内存因果暂停冻结证明通过', '酷狗数值内存因果Seek证明通过',
):
    if token not in source: fail.append('accuracy/recovery token missing: '+token)
if "LIMBUSLYRIC_QQ_RAIL_VISUAL_DIRECT', '0'" not in source:
    fail.append('software-2 rail visual-direct default is not 0')
if 'self._start_auto_local_clock(self._qq_gesture_expected_ms)' in source:
    fail.append('rail geometry is still allowed to start a lyric clock')
if "QQ_LYRIC_TEXT_SEEK_ENABLED and self._uia_has_lock" not in source:
    fail.append('cold-start heavy lyric-text probe deferral missing')

if fail:
    print('QQ STARTUP AUTHORITY FIX ACCURACY/RECOVERY: FAIL')
    for x in fail: print('  - '+x)
    raise SystemExit(32)
print('QQ + KUGOU CAUSAL CLOCK GUARD ACCURACY/RECOVERY: PASS')
print(f'  source-identical software-2 authority methods locked: {len(SOFTWARE2_LOCKED)}')
print(f'  reviewed QQ text-boundary methods locked: {len(QQ_TEXT_BOUNDARY_REVIEWED)}')
print(f'  reviewed accuracy/recovery functions locked: {len(SAFE_FASTSTART_PATCH)}')
print('  QQ Text adapter remains exact; outer merge/edge/reset are v138 reviewed boundary-clock changes')
print('  rail geometry cannot drive provisional/formal lyric time: PASS')
print('  QRC race + wake retry + software-2 locks + host stale guard + independent raw GSMTC witness + rail handoff suppression + fast initial PLL trust + post-bind QQ duration identity refresh + display-only fast provisional seed + startup stale-handoff guard + pre-lock rail validated anchor + no-fake-zero wait + sandbox seek/restart authority + KuGou outer causal publication guard + symmetric safe full-lyric fallback: PASS')
