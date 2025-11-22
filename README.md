ถ้าในเครื่องยังไม่มี poppler ให้ติดตั้ง poppler ก่อน

1.  **ดาวน์โหลด Poppler:**
    * เข้าไปที่ลิงก์: `https://github.com/oschwartz10612/poppler-windows/releases/` 
    * มองหา **Release 25.11.0-0** หรือ Version ล่าสุด
    * คลิกที่ **`Release-25.11.0-0.zip`** เพื่อดาวน์โหลดไฟล์ 

2.  **ตั้งค่า Path Environment Variable:**
    * แตกไฟล์ 
    * คลิกเข้าไปในโฟลเดอร์ที่ถูกแตกออกมา แล้วค้นหาไฟล์ **`bin`** 
    * หลังจากเจอไฟล์ `bin` ให้ **Copy Path** เพื่อนำไปใส่ใน Path system environment variables 
    * ไปที่เมนู **"Windows Search"** หรือ **"Search Box"** แล้วเสิร์ชว่า **`Edit the system environment variables`**
    * คลิกไปที่ **`Environment variables`** 
    * ในเมนู **System variables** ค้นหาคำว่า **`PATH`** 
    * กด **Edit** หลังจากนั้นกด **New** แล้วให้ใส่ path ที่ copy ไว้ก่อนหน้าได้เลย 
    * กด **OK** 

---

ดำเนินการติดตั้งโปรเจกต์ตามขั้นตอนด้านล่างนี้:

1.  **Clone Repository:**
    * `git clone xxxxxxXXXXXXXXXXX` 

2.  **ตั้งค่า Environment:**
    * สร้างไฟล์ **`.env`** 
    * ใส่ API key ที่จำเป็นลงในไฟล์ `.env`
    * ไปที่ `https://playground.opentyphoon.ai` เมื่อลงชื่อเข้าใช้แล้ว คลิก API key ที่มุมขวาบน แล้วนำมาใส่ใน `OPENAI_API_KEY`
    
```
OPENAI_API_KEY=""
GOOGLE_API_KEY=""
```
3. **ติดตั้ง Qdrant**
    * pull docker image 
        * `docker pull qdrant/qdrant`  

    * run ที่ root folder
        * `docker run -p 6333:6333 -v ./qdrant:/qdrant/storage qdrant/qdrant`

4.  **การติดตั้ง Dependencies และเปิดใช้งาน Virtual Environment:**
    * ใช้เครื่องมือ `uv` ในการเริ่มต้น (Initialize):
        * `uv init` 
    * เปิดใช้งาน Virtual Environment:
        * `.venv\Scripts\activate` 
    * ติดตั้ง Dependencies ตามไฟล์ `requirement.txt`:
        * `uv pip install -r requirement.txt` 

---

รันโปรเจกต์

### 1. รัน Backend

* รันเซิร์ฟเวอร์ Backend (uvicorn) ที่พอร์ต 8000:
    * `uvicorn main:app --port 8000 --reload` 

### 2. รัน Frontend

* ย้ายไปที่ไดเรกทอรี `frontend`:
    * `cd frontend` 
* รัน Frontend Server:
    * `npm run dev` 