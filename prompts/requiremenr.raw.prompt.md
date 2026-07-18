# วิเคราะห์ และ ออกแบบ
## จำไว้ออกแบบโดยละเอียดที่สุด โดยยึด Requirement สำคัญห้าม เยิ่นเย้อ อะไรนอกเหนือ Requirement ตัดออกให้หมด ต้องกำชับลงใน Prompt ให้เรียบร้อย หาก Prompt มีขั้นตอนเยอะมากๆ จะต้อง Chunk Prompt ออกไปเป็นส่วนได้ แต่ต้องไม่เสียความหมาย หรือทำให้ Agent เข้าใจผิดในการดำเนินการ แม้แต่นิดเดียว

## Requirement ฉันบางอันมันอาจจะทับกัน แต่ให้สรุปแล้วรวมกันออกมาอย่างเหมาะสม ไม่แน่ใจให้ List และถามเพื่อรวมความเข้าใจ

## รูปแบบการใช้งาน Skill ควรเป็นแบบ ปลอดภัยในเรื่องการกำหนด user/pwd ของ Db ให้ได้มาตรฐานด้วยเผื่อีการนำไปใช้งานจริง โดยบุคคลอื่น ๆนอกจากฉัน

ช่วยคิดชื่อหน่อย ฉันทำ agrimap-agent-skills และเจอว่า เราขาดเราเตรียมข้อมูลให้
เอไอ มันเลยทำงานออกมาได้ไม่ค่อยตรง หรือไม่รู้บริษัทในแง่ของฐานข้อมูล ฉันเลยสงสัยว่าถ้าทำ db-dump-skills เพื่อ dump table / store procedure ของ SQL ออกมาจากนั้นจัด format ด้วย sqlfluff แล้ววิเคราะห์ context การเชื่อมโยง เพื่อจัดหมวดหมู่ให้กับ sql ด้วย
เช่น UM_USER / UM_UROLE / CONTENT / CONTENT_SHARE_*

จะได้ 2 กลุ่ม คือ um และ content จะได้ 2 folder
- um
    - tables
      - UM_USER.sql
      - UM_ROLE.sql
   - store_procedures
      - UM_USER_I.sql
      ..
- content
   - tables
     - CONTENT.sql
     - CONTENT_SHARE.sql
   - store_procedures
     - CONTENT_I.sql
     ..

ออกมาเป็น output ตาม root project หรือไม่ ก็กำหนดได้ว่าจะ Out put ไว้ที่ไหน จาก context เช่น เขียนไป ที่ xxx หรือ output xxx หรือ สร้างที่ xx นะ แบบนี้ก็ได้

ส่วนที่ละเอียดกว่านั้น คือ ใน sql ที่ dump ออกมาจะต้องมีข้อมูลประกอบด้วย อย่างน้อย ตารางละ 10 รายการ เพื่อเป็นต้นแบบให้ model เข้าใจแนวทางข้อมูลมากขึ้น มากกว่าเดาสุ่ม เพื่อความแม่นยำในการใช้งาน 

และนี่คือ Spec ของ WebServer / MCP Server เพื่อบริการ Dump ข้อมูล SQL ตรงนี้ต้องออกแบบแนวทาง + Logic ที่ใช้งาน เพื่อความปลอดภัย โดย Agent หรือ Model ไม่รู้ User/Pwd สำหรับ Connect DB ผู้ใช้งานจะต้องเป็นคนกำหนด และ Run ไว้ล่วงหน้าเอง แต่ Script ุชุดนี้ต้องสร้างได้จาก Prompt นี้ โดยกำหนดให้เลือกใช้ python / nodejs เป็นหลัก Model  สามารถวางแผนออกแบบ Trade-off ตัวที่เหมาะสมได้เลยพร้อมเหตุผล ว่า เพราะอะไรจึงเลือกตัวนี้ และไม่เลือกอีกตัว --> สเปคการออกแบบ Logic จะต้อง มี ชื่อ Function / API สำหรับบริการพร้อมรายละเอียดชัดเจน ว่า HTTP Behavior / HTTP URL / INPUT / OUTPUT ตัวอย่างให้เห็นและคาดเดาผลลัพธ์ได้ แล้วแต่ว่าเป็น API หรือ MCP --> สำคัญมากการ Dump ข้อมูลออกมาแล้วต้องรองรับ Cleansing ข้อมูลที่ Sensitive โดยเช่น 
ID Card / Username / Password / SecretKey / JWT / Refrest Token / ข้อมูลความลับ จะต้อง Fill Marked ก่อนออกมาเป็น Input เช่น 1102001xxxxxx หรือ Password  dPtv2oGEZLFvC3G1yiftC... แทนเป็นต้น ฐานข้อมูล บางทีมีเป็น 100-1000 การออกแบบต้องคำนึงถึง performance ด้วยเช่น รองรับ batch แต่ต้องสัมพันธ์กับ skill ด้วยคือ skill ต้องรู้ว่าต้องรัน กี่รอบ และปั้น paging ยังไงเพื่อให้ข้อมูลที่ได้กลับมาครบถ้วน อย่างเช่นอาศัย API ที่บอก sitemap เป็นต้น

ส่วนสเปคของ Skill ชุดนี้ จะต้องเรียกใช้เครื่องมือด้านบนได้อย่างชาญฉลาด เข้าใจ
และเรียบร้อยข้อมูลกลุ่มได้อย่างสมเหตุสมผล ส่วนไหนไม่รู้จริง ๆ ห้ามเดา ให้ถาม Owner พร้อม บอก category ทั้งหมด เพื่อตัดสินใจจะจัดเก็บลงตรงไหน ในการวิเคราะห์แล้วจะต้องทข้อมูล Tags หรือ Index บางอย่างเพื่อให้สามารถนำมาใช้ประโยชน์อื่นได้ เช่น การวาด ER-Diagram การแสดงเส้นความสัมพันธ์ เช่น 1..M to M..N เป็นต้น และที่สำคัยรองรับการสร้าง grahpy สำหรับดู tree ว่าตารางนี้เชื่อมโยงไปที่ไหนได้ด้วยแบบเป็น phase ถัดไป ง่าย ๆคือการออกแบบรับความขยับขยาย

เพิ่มเติม Spec อีกเล็กน้อย เครื่องมือการ Lint /Format ให้ใช้ python sqlfuff โดยจะต้อง auto install หากเช็คในขั้นตอนติดตั้งแล้วไม่พบเครื่องมือ โดยติดตั้งครั้งเดียวพอ แต่มีสกิลสั่ง อัปเดต sqlfuff version ได้ในตัว

จากการบอกเล่าทั้งหมด ฉันอยากให้คิดชื่อเพื่อสร้าง github ด้วย มันเกิดมาเพื่อทำงานร่วมกับทุกโปรแกรมได้ไม่จำเป็นต้องเป็น AgriMap ให้รองรับการทำงานหลัก กับ sql ดังนี้

sqlserver -> tsql
mysql -> ??
mariadb -> ??
oracle (รุ่นใหม่) -> ??
postgresql -> psql

โดยมีการ Mapping รายละเอียดการใช้งานใน DB ให้เรียบร้อย

spec เพิ่มสำหรับการใช้งาน sqlfuff

 ใช้แบบนี้ได้เลย เป็นตัวจัด format

  # กรณีหลายไฟล์ใน folders
  sqlfluff format --exclude-rules "CP02, LT01, RF06" --dialect tsql .

  # กรณีไฟล์เดียว
  sqlfluff format --exclude-rules "CP02, LT01, RF06" --dialect tsql XXXXX.sql

  แต่ agent / model ต้องเข้าใจ กรณี error ฉันเจอว่ามันจะหยุด parser ทันที หากมีหลายไฟล์ เมื่อเจอไฟล์ที่กำลังแก้พัง

.tmp-sql-finalizer/sql/UM/procedure/ — โครงสร้างซ้อนแต่ว่างเปล่า
  .tmp-sqlfluff-format/ — ว่างเปล่า
  น่าจะเป็นซากจากการทดสอบ SQL finalizer / SQLFluff format ของงานเวอร์ชัน 0.1.4 ที่ลบไม่หมด ตอนนี้ git มองไม่เห็น (directory ว่าง)
  แต่ทั้งสองชื่อไม่อยู่ใน .gitignore — ถ้ามีการรันครั้งหน้าแล้วเขียนไฟล์ลงไป จะโผล่เป็น untracked ทันที

  ข้อเสนอ: ลบทั้งสอง directory ทิ้ง และ/หรือเพิ่ม .tmp-*/ ลง .gitignore เพื่อกันเครื่องมือทิ้งซากในอนาคต — บอกได้เลยถ้าต้องการให้จัดการ

 พวก folder tmp แบบนี้ไม่ควรเกิดขึ้นตอนที่เอาไปใช้งานนะ


 และ makesure ไหม ถ้าติดตั้ง plugins แล้วเครื่องไม่มี sqlstuff มันจะลงให้

# Note
1. เพิ่มเติมอีกนิด ในส่วนของ Feature ที่ว่า แยก Classify ข้อมูลออกเป็นหมวด User สามารถเลือกได้ แต่อาจจะมี mode ถามก่อน สร้างให้หน่อยก็ได้ว่าต้องการ เลือกบางหมวด หรือสร้างทั้งหมด เพราะ MCP/API คืนกลับมามันเป็นแค่ชื่อ แต่ในชื่อมันบอก หมวดและ บริบทเบื้องต้น แต่บางอันอาจจะไม่ซะทีเดียว Model ต้องมีกระบวนการคิด 2 ชั้น 1. ชั้นแรก จำแนกกลุ่มเบื้องต้น ผู้ใช้เลือก ยังไงก็ต้อง dump มาทั้งหมด แล้วค่อยวิเคราะห์ความสัมพันธ์ จากนั้นตัดออกอีกรอบ เพื่อป้องกัน ชื่อ กำกวม ชื่อไม่สื่อความหมาย แต่จริงๆ อยู่หมวดเดียวกัน 

2. Model ต้องอัปเดต Changlog และ Increse version ได้เองเมื่อมีการปรับแปก้ไข

3. มีคู่มือการใช้งาน ตั้งแต่การ Run MCP และ ใช้งาน Skills แบบ case by case

4. คู่มือในส่วนของคำสั่ง ต้องเตรียม studies case ไว้ให้ใน ตาราง exmaples ด้วย พร้อม case 2-3 เคสจากแต่ละเรื่องถ้าสามารถทำได้ เพื่อให้ผู้ใช้งานเข้าใจง่ายขึ้น

5. ต้องรองรับการทำงานร่วมกับ harness & model ของค่าย 3 ค่ายนี้เป็นหลัก codex, claude, gemini 

# Note เพิ่มเติมจากการตรวจสอบความสอดคล้อง — ห้ามแก้หรือลบ Requirement เดิมด้านบน

6. ต้องกำหนดจังหวะการใช้ SQLFluff ให้ชัดเจน โดย Version 1 ให้รัน SQLFluff เฉพาะไฟล์ SQL ที่อยู่ใน final materialization หลัง Pass 2 และ Owner resolution เสร็จแล้วเท่านั้น ห้าม format object ทั้งหมดใน full analysis เพราะการวิเคราะห์ความสัมพันธ์ใช้ sanitized SQL/metadata ที่ยังไม่ format ได้ วิธีนี้ลด cost และทำให้ตัวเลข SQLFluff ใน manifest นับเฉพาะไฟล์ที่ materialize จริง ตัวอย่างกรณี materialized 214 files ต้องมีสมการ `format_requested = formatted + parse_failed_preserved + format_failed_preserved = 214` ส่วน 4 objects ที่ analysis fail ต้องไม่ถูกนับรวมใน format scope

7. HTTP และ MCP ต้องสมมาตรใน operation/resource ที่ประกาศให้เทียบ contract กันได้ หาก MCP มี `sqlctx://export/{export_id}/report` ต้องมี HTTP `GET /api/v1/exports/{export_id}/report` ที่คืน structured report เดียวกัน และ contract test ต้องเทียบ normalized result ได้

8. Version ของรูปแบบ Output ให้ใช้ชื่อ canonical เพียงชื่อเดียวคือ `output_format_version` ทุกจุด ใน manifest ใช้ `output_format_version` และ validation input ใช้ `expected_output_format_version` ห้ามสร้าง `format_version`, `expected_output_layout_version` หรือ layout version แยกใน Version 1

9. Deterministic masking alias ต้องระบุการ map จาก HMAC ให้เป็นรูปแบบ alias จริง ห้ามใช้ sequence ธรรมดาที่ขึ้นกับลำดับ query ตัวอย่างให้ใช้ `digest = HMAC-SHA256(snapshot_masking_key, normalized_value)` แล้ว encode digest prefix เป็น Base32 token เช่น `user_k7m2q9x4p1` และ `user_k7m2q9x4p1@example.invalid` ต้องมี per-snapshot alias registry สำหรับตรวจ collision และ resume ข้าม process โดยเก็บใน protected runtime store ห้าม export raw value, masking key หรือ registry ลับออกมา หากใช้ owner stable key จึงจะคง alias ข้าม snapshot ได้

10. Endpoint ที่ paginated ต้องมี envelope แบบเดียวกันทุกตัว ตัวอย่าง `classification-requests` ต้องมี `items` และ `page: {limit, returned, next_cursor}` และ Skill ต้องอ่านจน `next_cursor = null` นอกจากนี้ workflow หลักกับ Chunk prompt ต้องมีขั้นตอนเท่ากัน โดยต้องระบุ `Write reports and manifest` เป็นขั้นตอนชัดเจนก่อน cleanup และ final report

11. Job lifecycle ต้องครบสำหรับ resumability และ cancellation ต้องเพิ่ม paginated list operations สำหรับ catalogs และ exports เพื่อ rediscover งานเดิมหลัง session ขาด เพิ่ม cancel operations สำหรับ catalog/export และให้ cancellation เป็น cooperative/idempotent โดยส่งต่อไปยกเลิก database query เมื่อ adapter รองรับ ห้ามประกาศ status `cancelled` หากไม่มี operation ที่ผู้ใช้หรือ Skill เรียกได้

12. Sanitized catalog snapshot, checkpoints, export bundles และ reports ใน runtime store ต้องมี retention policy และ disk quota ค่า default คือ completed catalog 24 ชั่วโมง, completed export artifacts 24 ชั่วโมง และ runtime store รวมไม่เกิน 5 GiB โดยปรับค่าได้ Active job ห้ามถูกลบอัตโนมัติ ต้อง cleanup expired completed artifacts ก่อนรับงานใหม่ หากพื้นที่ยังไม่พอให้ตอบ `507 RUNTIME_STORAGE_FULL` ห้ามลบงาน active หรือ artifact ที่ยังไม่หมดอายุแบบเงียบ ๆ และต้องมี owner-authorized delete operation สำหรับ catalog/export เพื่อ cleanup ทันที

13. Local bearer token handoff ต้องไม่คลุมเครือ เมื่อ start server ให้สร้าง random token และ connection metadata ใน user runtime directory ที่ permission เป็น owner-only (`0600` บน POSIX และ ACL เฉพาะ current user/SYSTEM บน Windows) stdout แสดงได้เฉพาะ MCP URL กับ path ของ connection metadata ห้ามพิมพ์ token ตัวจริง Harness configuration และ `sqlctx` CLI ให้อ่าน token ผ่าน owner-approved configuration/bootstrap command โดย Skill/Model ห้ามอ่าน แสดง หรือส่ง token เป็น tool argument/command-line argument

14. Idempotency ต้องนิยามเป็น contract สำหรับ create catalog และ create export ฝั่ง HTTP ใช้ required `Idempotency-Key` header ส่วน MCP ใช้ required `idempotency_key` field ทั้งสองต้องเข้า application model เดียวกัน Key เดิม + normalized request เดิมต้องคืน job เดิม Key เดิม + request ต่างกันต้องตอบ `409 IDEMPOTENCY_CONFLICT` ต้อง scope key ตาม caller + operation และเก็บ record ตาม retention policy

15. การส่ง ZIP bundle ให้ Skill ใช้กลไกเดียวใน Version 1: HTTP binary endpoint ที่ถูกเรียกผ่าน deterministic `sqlctx export fetch --export-id ...` helper/CLI เท่านั้น CLI อ่าน bearer token จาก owner-only connection metadata ภายใน process ห้ามส่ง token ใน prompt หรือ command line MCP คืนเฉพาะ export ID, size, hash, status และ manifest/report ขนาดเล็ก ห้ามส่ง ZIP/base64 ผ่าน MCP resource และห้ามคืน unrestricted local runtime path ให้ Model หลัง download ให้ validate size/hash/manifest/path traversal ใน OS temp ก่อน assemble เข้า project

16. ต้องกำหนด Python ขั้นต่ำเป็น `>=3.11` ใน `pyproject.toml` และสร้าง CI จริงใน `.github/workflows/ci.yml` ตั้งแต่ repository skeleton โดย CI ต้องรัน formatting, lint, type check, unit, contract, integration, E2E และ harness simulator ตาม phase ที่มี implementation แล้ว ห้ามเขียน Acceptance ว่า CI รันทุก commit แต่ไม่มี Chunk ไหนสร้าง workflow

17. Version ระหว่าง build กับ release ต้องแยกกัน ช่วง Chunk implementation ให้เริ่ม `0.1.0-dev.0` และเพิ่ม pre-release sequence หนึ่งครั้งต่อ Chunk ที่เสร็จ เช่น `0.1.0-dev.1` พร้อมอัปเดต `CHANGELOG.md` ส่วน `1.0.0` ให้ bump ครั้งเดียวใน final release gate หลัง mandatory tests ผ่านทั้งหมด การแก้ย่อยภายใน Chunk ให้อยู่ใน changelog ของ Chunk เดียวกัน ห้าม bump patch/minor แบบ release ทุกครั้งจนเลข release drift

18. Prompt implementation ต้องเก็บ specification ฉบับ authoritative แบบ byte-for-byte ไว้ใน implementation repository ที่ `docs/spec/design-spec-v1.3.md` พร้อม hash ห้ามให้ Agent เรียบเรียง immutable contract ใหม่เอง ทุก Chunk ต้องระบุ section ที่ต้องอ่านจากไฟล์นี้และอ่าน `docs/implementation-state.md` เพื่อรับช่วงงาน ห้ามโหลด spec ทั้งไฟล์โดยไม่จำเป็น และห้ามใช้ v1.1/v1.2 เป็น source of truth เมื่อ v1.3 มีแล้ว

19. ให้รันหนึ่ง Chunk ต่อหนึ่ง fresh Agent session ไม่ใช้ same session ยาวตลอดทุก Chunk เพราะเสี่ยง context ล้นและ instruction drift แต่ละ session ต้องอ่านเฉพาะ immutable invariants, section ที่ Chunk ระบุ, implementation state, changelog และไฟล์ code ที่เกี่ยวข้อง หาก Chunk ใหญ่ให้แยกเป็น sub-chunk ได้ โดยเฉพาะ database adapters 5 engines และ cross-harness conformance

20. ระหว่างสร้าง v1.3 ให้ใช้ Requirement raw ฉบับนี้ร่วมกับ v1.2 เพื่อทำ diff เท่านั้น ห้ามป้อน v1.1 ควบคู่เป็น authoritative context หลังสร้าง v1.3 แล้ว implementation session ต้องใช้ v1.3 ฉบับเดียว ส่วน raw/v1.1/v1.2 เป็น archive/traceability เท่านั้น

21. ตัด optional feature ที่ไม่มีใน Requirement เดิมออกจาก Version 1 ได้แก่ `sample_strategy: relationship_aware` และ `dependency_materialization: direct/closure` ให้ sampling ใช้ deterministic strategy เท่านั้น และ selective output เก็บความสัมพันธ์ของ object ที่ไม่ได้ materialize เป็น boundary/index metadata แบบ `index_only` คงที่ ไม่ต้องเปิดเป็น user-selectable mode

22. ห้ามเดาหรือระบุชื่อ Model ที่สร้าง specification จากสำนวนหรือคุณภาพของไฟล์ หากไม่มี metadata ที่ตรวจสอบได้ ให้รายงานได้เฉพาะผลการตรวจคุณภาพและข้อผิดพลาดเชิงหลักฐาน

23. จำนวน token ของ specification ขึ้นกับ tokenizer และรุ่น model ห้าม hardcode ตัวเลขประมาณการเป็นข้อเท็จจริง ให้ลด cost ด้วย spec-in-repo, section routing, fresh session และวัด token ด้วย tokenizer ของ target harness เมื่อจำเป็น

# Change Log — v1.4 Cut-off / Product 1.0.0 Development Baseline

รายการต่อไปนี้เป็นข้อกำหนดที่แทรกเพิ่มจาก final review โดยไม่ลบหรือแก้ Requirement เดิม หากข้อความขัดกับข้อก่อนหน้า ให้ข้อที่มีเลขมากกว่าใน Change Log นี้เป็น authoritative clarification สำหรับ v1.4

24. Snapshot ที่ resume ข้าม process ต้องใช้ `snapshot_masking_key` เดิมตลอดอายุ snapshot ห้ามสร้าง key ใหม่ตอน resume ให้เก็บ key แบบ encrypted/protected ใน runtime store โดยผูกอายุกับ catalog และ dependent exports หรือ derive จาก owner-held secret แบบ deterministic หาก host ไม่สามารถเก็บ key อย่างปลอดภัยต้องประกาศ snapshot ว่า resume ข้าม process ไม่ได้ ห้ามแกล้งรายงานว่า resumable Key, raw value และ secret registry ห้ามเข้า export/model context

25. SQLFluff ทุกคำสั่งต้องรันผ่าน interpreter ของ managed runtime ที่ active/pinned อย่างชัดเจน เช่น `<selected-runtime-python> -m sqlfluff` ห้ามใช้ bare `python -m sqlfluff` ใน production orchestration แต่ละ export job ต้อง pin runtime ID/version ตั้งแต่เริ่ม Update เปลี่ยน active pointer สำหรับงานใหม่เท่านั้นและห้ามสลับ runtime ใต้งานที่กำลังรัน

26. Category preview ต้องใช้ standard paginated envelope `items` และ `page: {limit, returned, next_cursor}` เหมือน HTTP/MCP tools ทุกหน้า Skill ต้องอ่านจน `next_cursor = null` สำหรับ MCP ให้ใช้ paginated tools เป็น canonical traversal และตัด paginated catalog resources ที่ไม่มี cursor/limit/view ออก เหลือ resource เฉพาะ manifest/report ขนาดเล็กที่ไม่ต้องแบ่งหน้า

27. Catalog/export rediscovery descriptor ต้องมี `request_fingerprint` จาก canonical normalized non-secret request และมี safe request summary ที่เพียงพอให้ตัดสิน exact match เช่น schemas, filters, sample/masking/selection policy, catalog ID และ object-batch fingerprint ห้าม resume จาก profile/status อย่างเดียว หาก fingerprint ไม่ตรงต้องไม่ reuse job เดิม

28. Version 1 ห้าม client ปิด mandatory export stages ให้เอา `sqlfluff` และ `append_samples` Boolean switches ออกจาก public export request หรือ validate เป็น literal `true` และ reject `false` โดย explicit error Formatting final-materialization SQL และการ append sample metadata/rows ตาม policy เป็น invariant

29. Completed `ExportStatus` ต้องคืน immutable integrity metadata อย่างน้อย `size_bytes`, bundle `sha256`, `manifest_sha256`, output format version และ artifact URLs/IDs ทั้ง HTTP และ MCP ต้องได้ normalized ค่าเดียวกัน เพื่อให้ `sqlctx export fetch` ตรวจ size/hash ก่อนและหลัง download

30. Final validation ต้องตรวจไฟล์ที่ assemble อยู่ใน project จริง ไม่ใช่ตรวจเฉพาะ server-side bundle ให้ `sqlctx validate output --root ...` อ่าน managed files จาก destination ใหม่ สร้าง relative-path/size/SHA-256 inventory และส่ง inventory/digest เข้า validation contract เพื่อเทียบกับ export manifests ห้ามส่ง unrestricted root path ให้ server/model และห้าม claim completion หาก assembled inventory ไม่ตรง

31. Owner-authorized operations ต้องบังคับสิทธิ์แยกจาก harness agent token ได้แก่ delete, persistent classification resolution/override, SQLFluff update, remote enablement และ masking-policy weakening ให้ใช้ owner credential ที่ไม่ส่งให้ harness ร่วมกับ short-lived one-time approval ซึ่ง bind กับ caller, operation, target และ normalized request digest Agent token อย่างเดียวต้องได้ `APPROVAL_REQUIRED`/`403` และทำ operation ไม่สำเร็จ

32. Retention ของ catalog ต้องต่ออายุหรือถูก pin ตราบใดที่ dependent export ยัง active หรือยังไม่หมดอายุ ห้าม cleanup snapshot, checkpoint, masking key/state หรือ alias registry ใต้ export ที่ยังใช้งาน Cleanup catalog ได้เมื่อไม่มี active/unexpired dependent export หรือ owner ลบ dependency ตามลำดับอย่างชัดเจนเท่านั้น

33. Release gate ต้องเป็นสองช่วง: Phase A pre-release gate รัน mandatory tests/docs/security บน `1.0.0-dev.N`; เมื่อผ่านจึง Phase B เปลี่ยน version ทุก surface เป็น `1.0.0` และเพิ่ม release entry ใน `CHANGELOG.md` แล้ว rerun version consistency, package/build และ release smoke tests ห้ามกำหนดให้ changelog มี release entryก่อน Phase A ผ่าน

34. v1.4 เป็น specification cut-off และเป็น source of truth เดียวสำหรับเริ่มพัฒนา Product target คือ `1.0.0`; ระหว่าง implementation ใช้ `1.0.0-dev.0`, `1.0.0-dev.1`, ... ตาม Chunk แล้วจบที่ `1.0.0` หลัง Phase B ผ่าน ข้อนี้ supersede ค่าเริ่ม `0.1.0-dev.N` ในข้อ 17 โดยไม่ลบประวัติเดิม

35. ต้องเก็บ v1.4 แบบ byte-for-byte ที่ `docs/spec/design-spec-v1.4.md` พร้อม `design-spec-v1.4.sha256` และเปลี่ยน section routing ของทุก implementation Chunk ให้อ่าน v1.4 เท่านั้น v1.3 และเก่ากว่าเป็น archive/traceability

36. ก่อนประกาศ cut-off ต้องรัน consistency checks อย่างน้อย: HTTP contract map เท่ากับ Chunk endpoint list, MCP tool/resource map เท่ากับ Chunk, paginated envelopes มี cursor termination, main workflow เท่ากับ Skill Chunk, JSON/YAML examples parse ได้, release gate ไม่มี circular dependency และไม่มี public switch ที่ปิด mandatory invariant

37. Product version สำหรับเริ่มพัฒนาและพร้อมปล่อยให้ใช้ `1.0.0` ทันที ห้ามใช้ `-dev.N` หรือ pre-release suffix หากระหว่างพัฒนาหรือทดสอบพบข้อแก้ไขให้ bump patch เป็น `1.0.1`, `1.0.2`, ... พร้อมอัปเดตทุก version surface และ `CHANGELOG.md` แล้วรัน gate ใหม่ การ bump minor ใช้เมื่อเพิ่ม backward-compatible feature หรือมีการตัดสินใจขยาย scope และ major ใช้เมื่อ public contract แตก ข้อนี้ supersede วิธี version ในข้อ 17, 33 และ 34 เฉพาะส่วนที่กำหนด `0.1.0-dev.N`, `1.0.0-dev.N` หรือการเปลี่ยนเป็น `1.0.0` ตอนท้าย โดยยังคงหลัก two-phase gate: Phase A ทดสอบ current release version; หากผ่าน Phase B finalize artifact/changelog ของ version เดิมและ rerun release checks โดยไม่เปลี่ยน version

# Change Log — v1.5 / Product 1.0.1 Host-Python Runtime Correction

รายการต่อไปนี้เป็น authoritative clarification ที่มีลำดับใหม่กว่าและ supersede ข้อความเรื่อง managed runtime/runtime ID/active pointer ในข้อ 25 รวมถึง source-of-truth/version ที่อ้าง v1.4/1.0.0 ในข้อ 35 และ 37 เฉพาะส่วนที่ขัดกัน โดยคงข้อความเดิมทั้งหมดไว้เป็นประวัติ

38. Production Skill และ SQLFluff ต้องใช้ Python interpreter ที่ติดตั้งอยู่บนเครื่องผู้ใช้เป็นหลัก โดย default ใช้ `sys.executable` ของ process ที่รัน `sqlctx` หรือ absolute interpreter ที่ Owner กำหนดใน configuration และต้องเป็น Python `>=3.11` ห้าม Skill, plugin, server bootstrap หรือ tooling manager สร้าง, copy, activate หรือจัดการ virtual environment/venv/conda/pipx environment ภายใน Skill directory, target project หรือ sqlctx runtime directory เด็ดขาด Owner จะเลือก environment ที่สร้างเองอยู่ก่อนแล้วได้ แต่ sqlctx ต้องไม่ถือ ownership หรือแก้ environment นั้นอัตโนมัติ

39. SQLFluff ให้ตรวจและเรียกผ่าน host interpreter เดิมแบบ explicit `<host-python> -m sqlfluff` ทุกครั้ง หากไม่มี package ให้ขอ Owner approval ก่อนติดตั้ง pinned version ลง user site ของ interpreter เดิมด้วย `<host-python> -m pip install --user sqlfluff==<PINNED_VERSION>` ห้ามใช้ `sudo pip`, `--break-system-packages`, pipx หรือสร้าง environment ใหม่ หาก host Python/OS policy ไม่อนุญาต user-site install ให้คืน `TOOLING_UNAVAILABLE` พร้อมคำแนะนำ manual install ห้าม bypass policy การ update SQLFluff ต้อง reject ด้วย `409 TOOLING_BUSY` เมื่อมี export/format job active แล้วจึง update/verify/rollback version บน interpreter เดิมเมื่อ idle เพราะไม่มีหลาย managed runtime ให้ pin พร้อมกัน

40. หากไม่พบ Python `>=3.11` ให้ preflight/bootstrap script ที่ไม่พึ่ง Python คืน `PYTHON_UNAVAILABLE` และแสดง guideline ติดตั้งจาก official Python downloads หรือ OS package manager ที่ Owner อนุมัติ แยก Windows/macOS/Linux พร้อมคำสั่ง verify version, resolve absolute `sys.executable`, ตรวจ `pip`, ตรวจ user-site และ PATH ห้าม Skill ติดตั้ง Python ให้อัตโนมัติ หลังติดตั้งให้ Owner rerun preflight/doctor Product correction นี้ออกเป็น `1.0.1` และ specification v1.5 โดย v1.4 คงเป็น cut-off archive ห้ามแก้ย้อนหลัง
