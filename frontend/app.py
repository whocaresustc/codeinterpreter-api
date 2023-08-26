import asyncio
import sys

import os
import shutil
import tempfile


import streamlit as st  # type: ignore
from typing import Optional

from codeinterpreterapi import File
from codeinterpreterapi import CodeInterpreterSession
#from frontend import get_images
#from frontend.utils import get_images
async def get_images(prompt: str, files: Optional[list] = None):
    if files is None:
        files = []
    with st.chat_message("user"):
        st.write(prompt)
    with st.spinner():
        async with CodeInterpreterSession(model="gpt-3.5-turbo") as session:
            response = await session.generate_response(prompt, files=files)

            with st.chat_message("assistant"):
                st.write(response.content)

                # Showing Results
                for _file in response.files:
                    st.image(_file.get_image(), caption=prompt, use_column_width=True)

                # Allowing the download of the results
                if len(response.files) == 1:
                    st.download_button(
                        "Download Results",
                        response.files[0].content,
                        file_name=response.files[0].name,
                        use_container_width=True,
                    )
                else:
                    target_path = tempfile.mkdtemp()
                    for _file in response.files:
                        _file.save(os.path.join(target_path, _file.name))

                    zip_path = os.path.join(os.path.dirname(target_path), "archive")
                    shutil.make_archive(zip_path, "zip", target_path)

                    with open(zip_path + ".zip", "rb") as f:
                        st.download_button(
                            "Download Results",
                            f,
                            file_name="archive.zip",
                            use_container_width=True,
                        )

# Page configuration
st.set_page_config(layout="wide")

st.title("Code Interpreter API 🚀")

# This will create a sidebar
st.sidebar.title("Code Interpreter API 🚀")
st.sidebar.markdown("[Github Repo](https://github.com/shroominic/codeinterpreter-api)")


# This will create a textbox where you can input text
input_text = st.text_area("Write your prompt")
uploaded_files = st.file_uploader("Upload your files", accept_multiple_files=True)

uploaded_files_list = []
for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    uploaded_files_list.append(File(name=uploaded_file.name, content=bytes_data))

# This will create a button
button_pressed = st.button("Run code interpreter", use_container_width=True)

# This will display the images only when the button is pressed
if button_pressed and input_text != "":
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_images(input_text, files=uploaded_files_list))
    else:
        asyncio.run(get_images(input_text, files=uploaded_files_list))
