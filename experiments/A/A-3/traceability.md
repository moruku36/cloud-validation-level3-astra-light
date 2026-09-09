# 24要件 対応・判定表（修正後）

判定：設計上適合＝文書で求めた構造/方針を満たす、条件付き＝必要条件・仮定付き、未達＝現在の案で閾値違反が判明、未確認＝重要証拠が不足。どれも実測成功と同義ではない。
A-2箇所に[修正仕様](revised-design.md)、[予算訂正](budget.md)を優先適用。既存公式根拠は[A-2 sources](../A-2/sources.md)、追加根拠は[review](review.md)。全24件のクラウド実測は未実施。書類/算術検証は別欄。

|要件ID|判定|設計箇所・根拠/理由|検証方法|実測|
|---|---|---|---|---|
|REQ-01|設計上適合|[A-2](../A-2/design.md)＋[修正](revised-design.md)：AWS内3案、Bへの制約持込なし|資料確認|なし|
|REQ-02|条件付き|[A-2](../A-2/design.md)＋[修正](revised-design.md)：writer read・commit/冪等・本人次回参照、worker隔離|T01|なし|
|REQ-03|条件付き|[A-2](../A-2/design.md)＋[修正](revised-design.md)：メール非同期と除外機能を維持、再送重複未検証|T01,T08|なし|
|REQ-04|設計上適合|[A-2](../A-2/cost.md)＋[修正](revised-design.md)：登録者と要求倍率を分離|負荷式レビュー|なし|
|REQ-05|条件付き|[A-2](../A-2/cost.md)＋[修正](revised-design.md)：月2,835万API仮定とピーク100RPS、実トラフィック未確認|T02|なし|
|REQ-06|未確認|[A-2](../A-2/design.md)＋[修正](revised-design.md)：片AZ1taskでp95/エラー目標を満たす根拠なし|T02,T03|なし|
|REQ-07|未確認|[A-2](../A-2/recovery-operations.md)＋[修正](revised-design.md)：退会削除/復元再削除あり、42日PII台帳と35日消去保証が未確定|T06|なし|
|REQ-08|未確認|[A-2](../A-2/design.md)＋[修正](revised-design.md)：国内region指定、メール受信・managed内部保存転送先未確認|T07|なし|
|REQ-09|条件付き|[A-2](../A-2/recovery-operations.md)＋[修正](revised-design.md)：暦月E2Eと停止算入、synthetic精度/費用を修正|T03と継続月次測定|なし|
|REQ-10|未確認|[A-2](../A-2/recovery-operations.md)＋[修正](revised-design.md)：機構あり、全依存30分・配置/容量・起動時間は未証明|T03,T04|なし|
|REQ-11|未確認|[A-2](../A-2/recovery-operations.md)＋[修正](revised-design.md)：RDS同期の根拠あり、認証/画像含むデータ範囲は別評価|T04|なし|
|REQ-12|未達|[A-2](../A-2/cost.md)＋[修正](revised-design.md)：監視実行料追加で小計110,144円、予備費前に上限超過|予算算術、T09|なし|
|REQ-13|条件付き|[A-2](../A-2/recovery-operations.md)＋[修正](revised-design.md)：夜間即応は仮定しない。自動復旧外と日中工数が残る|T03,T10|なし|
|REQ-14|設計上適合|[A-2](../A-2/design.md)＋[修正](revised-design.md)：既存スキルとKubernetes不採用理由を反映|担当者レビュー|なし|
|REQ-15|条件付き|[A-2](../A-2/cost.md)＋[修正](revised-design.md)：1000RPS/100万人分離、増強条件は実測依存|T02,T09|なし|
|REQ-16|条件付き|[A-2](../A-2/design.md)＋[修正](revised-design.md)：role/暗号化/SG分離、ALB証明書・監査PIIの限界追記|T07,T08|なし|
|REQ-17|条件付き|[A-2](../A-2/design.md)＋[修正](revised-design.md)：3案比較あり、代替2案の価格根拠が弱く採用優位は未確定|比較見積レビュー|なし|
|REQ-18|条件付き|[A-2](../A-2/recovery-operations.md)＋[修正](revised-design.md)：OIDC/State/rollback方針、実現権限/再構築時間未確認|T05,T08|なし|
|REQ-19|設計上適合|[A-2](../A-2/design.md)＋[修正](revised-design.md)：指定配点・全閾値で初回/修正後採点、人間欄空欄|scores.md|なし|
|REQ-20|設計上適合|[A-2](../A-2/design.md)＋[修正](revised-design.md)：初回履歴・対応表・PR/Issue、秘密情報除外|リンク/remoteチェック|なし|
|REQ-21|設計上適合|[A-2](../A-2/design.md)＋[修正](revised-design.md)：今回A-3設計評価のみ（A-1文書の工程文言は履歴）|操作記録|なし|
|REQ-22|設計上適合|[A-2](../A-2/recovery-operations.md)＋[修正](revised-design.md)：C-0に予算/許可/期限を留保、今回資源なし|C-0承認後T11|なし|
|REQ-23|条件付き|[A-2](../A-2/recovery-operations.md)＋[修正](revised-design.md)：4hは暫定、隔離PITR・選択救済あり、時間と救済率未測定|T05|なし|
|REQ-24|条件付き|[A-2](../A-2/recovery-operations.md)＋[修正](revised-design.md)：大阪cold方針/損失/費用枠あり、認証復旧とコピー実効量不明|T05,T07|なし|

REQ-12根拠は[予算監査](budget.md)。REQ-19は[採点](scores.md)。T番号は[人間レビュー・C試験](validation-handoff.md)。環境適合の総合判定は未達/未確認を含み保留。書類作成要件の適合をクラウド合格数へ数え替えない。
