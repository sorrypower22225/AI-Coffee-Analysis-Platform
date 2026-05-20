import os
import sys
import importlib.util
import streamlit as st

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 確保套件資料夾可被 Python 匯入
for pkg in ["ui", "ui/pages", "utils", "services", "modules"]:
    init_path = os.path.join(BASE_DIR, pkg, "__init__.py")
    os.makedirs(os.path.dirname(init_path), exist_ok=True)
    if not os.path.exists(init_path):
        open(init_path, "a", encoding="utf-8").close()


def import_page_module(module_name: str, relative_path: str):
    """穩定載入頁面：一般匯入失敗時，直接用檔案路徑載入。"""
    file_path = os.path.join(BASE_DIR, relative_path)
    try:
        return __import__(module_name, fromlist=[""])
    except Exception as first_error:
        if not os.path.exists(file_path):
            raise ImportError(
                f"找不到頁面檔案：{file_path}\n原始錯誤：{first_error}"
            )
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"無法用檔案路徑載入：{file_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module


st.set_page_config(
    page_title="AI 咖啡營運分析平台｜作品集優化版",
    page_icon="☕",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
.block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)


def safe_run(page_name, module_name, relative_path, run_func_name):
    try:
        page_module = import_page_module(module_name, relative_path)
        run_func = getattr(page_module, run_func_name)
        run_func()
    except ImportError as e:
        st.error(f"❌ 無法載入「{page_name}」頁面")
        st.info("請確認你是執行這個新資料夾內的 app.py，不是舊資料夾。")
        st.code(str(e))
    except AttributeError as e:
        st.error(f"❌ 「{page_name}」頁面的函式名稱錯誤")
        st.info(f"請確認是否有 `{run_func_name}()` 這個函式。")
        st.code(str(e))
    except Exception as e:
        st.error(f"❌ 「{page_name}」執行時發生錯誤")
        st.code(str(e))


from utils.shared_data import sidebar_global_uploader

st.sidebar.title("☕ AI 咖啡分析平台")
sidebar_global_uploader()

menu = [
    "首頁",
    "預測分析",
    "儀錶板",
    "商品分析",
    "營業分析",
    "天氣分析",
    "展店分析 / 第四家店",
    "公式計算器",
]
choice = st.sidebar.selectbox("選擇頁面", menu)

if choice == "首頁":
    st.title("🏠 AI 咖啡營運分析平台｜作品集優化版")
    st.success("✅ 系統已啟動成功")
    st.info("已整合原始資料、清洗後特徵資料、Dashboard、AI 預測與展店分析。")
elif choice == "預測分析":
    safe_run("預測分析", "ui.pages.forecast", "ui/pages/forecast.py", "run_forecast_page")
elif choice == "儀錶板":
    safe_run("儀錶板", "ui.pages.dashboard", "ui/pages/dashboard.py", "run_dashboard_page")
elif choice == "商品分析":
    safe_run("商品分析", "ui.pages.analytics", "ui/pages/analytics.py", "run_analytics_page")
elif choice == "營業分析":
    safe_run("營業分析", "ui.pages.sales_analysis", "ui/pages/sales_analysis.py", "run_analysis_page")
elif choice == "天氣分析":
    safe_run("天氣分析", "ui.pages.weather_analysis", "ui/pages/weather_analysis.py", "run_weather_analysis_page")
elif choice == "展店分析 / 第四家店":
    safe_run("展店分析 / 第四家店", "ui.pages.expansion", "ui/pages/expansion.py", "run_expansion_page")
elif choice == "公式計算器":
    safe_run("公式計算器", "ui.pages.formula_calculator", "ui/pages/formula_calculator.py", "run_formula_calculator_page")
