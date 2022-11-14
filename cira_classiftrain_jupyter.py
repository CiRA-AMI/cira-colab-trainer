#!/usr/bin/env python
# coding: utf-8

# In[30]:


#@title Install CiRA Colab Trainer 

# Verbose
# !curl -sLf https://raw.githubusercontent.com/CiRA-AMI/cira-colab-trainer/main/boostrap.sh | bash && pip install ipywidgets ipyfilechooser

# No Verbose
import subprocess, time, os
ret = subprocess.call(['bash', '-c', 'curl -sLf https://raw.githubusercontent.com/CiRA-AMI/cira-colab-trainer/main/boostrap.sh | bash && pip install ipywidgets ipyfilechooser xattr && rm -rf cira-colab-trainer*'])
if ret != 0:
    print("CiRA Colab Trainer install error...")
else:
    print("CiRA Colab Trainer install complete")


# In[31]:


#@title Run test server in backgroud
if os.path.exists("/opt/colab/export"):
    ret = subprocess.call(['bash', '-c', 'rm -rf /opt/colab/export'])
    
subprocess.call(['bash', '-c', 'echo "exit" > /tmp/deepclassif_test.cmd'])
time.sleep(2)
subprocess.Popen(['bash', '-c', 'source /opt/ros/melodic/setup.bash && source /root/install/setup.bash && export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib && /root/install/lib/deepclassif_server/deepclassif_server_run --platform offscreen'])


# In[32]:


#@title Header

import json, time, os, subprocess, shutil, zipfile, rarfile, pathlib, datetime, base64
from threading import Timer
from ipywidgets.widgets.widget_string import Label, Text
from IPython.display import Javascript, JSON
from IPython.display import HTML as dHTML
from ipyfilechooser import FileChooser
from IPython import get_ipython

isColab = False

try:
    from google.colab import output
    from google.colab import files
    isColab = True
except:
    pass

from ipywidgets import (
    link,
    HTML,
    Button,
    Layout,
    Box,
    VBox,
    HBox,
    Checkbox,
    BoundedIntText,
    BoundedFloatText,
    IntSlider,
    FloatSlider,
    Dropdown,
    IntProgress,
    Accordion,
    Tab,
    Image
)

flexCol = Layout(
    display="flex", flex_flow="column", border="1px solid #a0a0a0", margin="2px", padding="5px"
)

wrapLayout = Layout(display="flex", flex_flow="wrap", grid_gap="8px", padding="0px")

js = Javascript("""
var kernel;
var isColab = false;
if (window.google != undefined) {
    kernel = window.google.colab.kernel;
    isColab = true;
} else {
    kernel = window.Jupyter.notebook.kernel;
}

function newApi(id, callback) {
    const comm = Jupyter.notebook.kernel.comm_manager.new_comm(id, {});
    comm.on_msg(msg => {
        const data = msg.content.data;
        callback(data);
    });
    return comm;
}
""")

def setup_comm_jupyter(api_call_id, callback):
    def _comm_api(comm, open_msg):
        @comm.on_msg
        def _recv(msg):
            ret = callback(comm, msg['content']['data'])
            comm.send(ret)
    get_ipython().kernel.comm_manager.register_target(api_call_id, _comm_api)

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


# In[33]:


#@title Dataset
fcImgFolder = FileChooser('/content')
fcImgFolder.title = '<b>Image Folder:</b>'
fcImgFolder.show_only_dirs = True
fcImgFolder.layout.max_height = '250px'

fcExtractFile = FileChooser('/content')
fcExtractFile.title = '<b>Extract zip/rar:</b>'
fcExtractFile.filter_pattern = ['*.zip', '*.rar']
fcExtractFile.layout.max_height = '250px'

def handleFcExtractFile(chooser:FileChooser):
    if chooser.selected is not None:
        btExtract.description = 'Extract'
        btExtract.disabled = False

fcExtractFile.register_callback(handleFcExtractFile)

btExtract = Button(description='Extract', disabled=True)


def onExtract(p):
    btExtract.description = 'Extracting...'
    btExtract.disabled = True
    file_extension = pathlib.Path(fcExtractFile.selected).suffix
    target_dir = pathlib.Path(fcExtractFile.selected).parent
    if file_extension == '.zip':
        with zipfile.ZipFile(fcExtractFile.selected) as archive:
            archive.extractall(target_dir)
    elif file_extension == '.rar':
        with rarfile.RarFile(fcExtractFile.selected) as rar:
            rar.extractall(target_dir)

    btExtract.description = 'Extract completed'

btExtract.on_click(onExtract)

datasetGroup = Box([fcExtractFile, btExtract, HTML("<h3 class='text-lg font-bold'>● Dataset</h3>"), fcImgFolder], layout=flexCol)


# In[35]:


# @title Augmentation
# rotation box
rotMinWidget = BoundedIntText(
    value=-180,
    min=-180,
    max=180,
    step=1,
    description="min:",
)
rotMinWidget.layout.width = '170px'

rotMaxWidget = BoundedIntText(
    value=180,
    min=-18,
    max=180,
    step=1,
    description="max:",
)
rotMaxWidget.layout.width = '170px'

rotStepWidget = BoundedIntText(
    value=90,
    min=1,
    max=360,
    step=1,
    description="step:",
)
rotStepWidget.layout.width = '170px'

rotCheckBox = Checkbox(value=True, description="Rotation", disabled=False, indent=False)
rotCheckBox.layout.width = '170px'
rotCheckBox.style.font_weight = 'bold'

rotationBox = Box(
    [
        rotCheckBox,
        rotMinWidget,
        rotMaxWidget,
        rotStepWidget,
    ],
    layout=flexCol,
)


def rotCheckedHandle(a):
    rotMinWidget.disabled = not a["new"]
    rotMaxWidget.disabled = not a["new"]
    rotStepWidget.disabled = not a["new"]


rotCheckBox.observe(rotCheckedHandle, names="value")

# contrast box
contrastMinWidget = BoundedFloatText(
    value=0.2,
    min=0.1,
    max=5,
    step=0.1,
    description="min:",
)
contrastMinWidget.layout.width = '170px'

contrastMaxWidget = BoundedFloatText(
    value=1.2,
    min=0.1,
    max=5,
    step=5,
    description="max:",
)
contrastMaxWidget.layout.width = '170px'

contrastStepWidget = BoundedFloatText(
    value=1.0,
    min=0.1,
    max=5,
    step=0.1,
    description="step:",
)
contrastStepWidget.layout.width = '170px'

contrastCheckBox = Checkbox(
    value=True, description="Contrast", disabled=False, indent=False
)
contrastCheckBox.layout.width = '170px'
contrastBox = Box(
    [contrastCheckBox, contrastMinWidget, contrastMaxWidget, contrastStepWidget],
    layout=flexCol,
)


def contrastCheckedHandle(a):
    contrastMinWidget.disabled = not a["new"]
    contrastMaxWidget.disabled = not a["new"]
    contrastStepWidget.disabled = not a["new"]


contrastCheckBox.observe(contrastCheckedHandle, names="value")

# noise box
noiseMaxWidget = BoundedIntText(
    value=10,
    min=1,
    max=999,
    step=1,
    description="max:",
)
noiseMaxWidget.layout.width = '170px'

noiseStepWidget = BoundedIntText(
    value=10,
    min=1,
    max=999,
    step=1,
    description="step:",
)
noiseStepWidget.layout.width = '170px'

noiseCheckBox = Checkbox(value=True, description="Noise", disabled=False, indent=False)
noiseCheckBox.layout.width = '170px'

noiseBox = Box(
    [noiseCheckBox, noiseMaxWidget, noiseStepWidget],
    layout=flexCol,
)


def noiseCheckedHandle(a):
    noiseMaxWidget.disabled = not a["new"]
    noiseStepWidget.disabled = not a["new"]


noiseCheckBox.observe(noiseCheckedHandle, names="value")

# blur box
blurMaxWidget = BoundedIntText(
    value=9,
    min=1,
    max=999,
    step=1,
    description="max:",
)
blurMaxWidget.layout.width = '170px'

blurStepWidget = BoundedIntText(
    value=9,
    min=1,
    max=999,
    step=1,
    description="step:",
)
blurStepWidget.layout.width = '170px'

blurCheckBox = Checkbox(value=True, description="Blur", disabled=False, indent=False)
blurCheckBox.layout.width = '170px'

blurBox = Box(
    [blurCheckBox, blurMaxWidget, blurStepWidget],
    layout=flexCol,
)


def blurCheckedHandle(a):
    blurMaxWidget.disabled = not a["new"]
    blurStepWidget.disabled = not a["new"]


blurCheckBox.observe(blurCheckedHandle, names="value")

augmentConfigGroup = Accordion(
    children=[
        Box([rotationBox, contrastBox, noiseBox, blurBox], layout=wrapLayout),
    ],
    selected_index = None,
)
augmentConfigGroup.set_title(0, 'Augmentation')


# In[36]:


# @title Gen training files box
modelDropdown = Dropdown(
    options=['darknet', 'darknet19', 'darknet19_448', 'darknet53', 'darknet53_448', 
             'densenet201', 'efficientnet-lite3', 'efficientnet_b0', 'mobilenet-v2', 
             'resnet101', 'resnet152', 'resnet18', 'resnet34', 'resnet50',
    ],
    value="mobilenet-v2",
    description="Model:",
)

batchSize = BoundedIntText(description="Batch size:", value=64, min=1, max=999, step=1)
batchSize.layout.width = "170px"
subDivisions = BoundedIntText(
    description="Sub divisions:", value=8, min=1, max=999, step=1
)
subDivisions.layout.width = "170px"

labelWarning = Label("Error file not found")
labelWarning.style.margin = "0"
labelWarning.style.padding = "0"
labelWarning.layout.visibility = "hidden"


def readLogGen():
    jso = {}
    jso["gen_progress"] = 0
    if os.path.exists("/tmp/classiftrain.log"):
        with open("/tmp/classiftrain.log", "r") as f:
            data = f.read()
            if data != "":
                jso = json.loads(data)
    return jso


def callTimerGen():
    jso = readLogGen()
    genProgress.value = jso["gen_progress"]
    genProgressLabel.value = str(jso["gen_progress"]) + "%"


def onGenerateClicked(p):
    btGenFile.disabled = True
    if fcImgFolder.selected is None :
        labelWarning.value = "Error: image folder not found."
        labelWarning.layout.visibility = "visible"
        btGenFile.disabled = False
        return

    if os.path.exists("/tmp/classiftrain.log"):
        os.remove("/tmp/classiftrain.log")

    labelWarning.layout.visibility = "hidden"
    genProgress.value = 0
    genProgressLabel.value = "0%"

    auto_gen = {}
    auto_gen["fh"] = False
    auto_gen["fv"] = False
    auto_gen["is_fh"] = False
    auto_gen["is_fv"] = False

    if rotCheckBox.value:
        auto_gen["is_rotate"] = True
        auto_gen["rotate_min"] = rotMinWidget.value
        auto_gen["rotate_max"] = rotMaxWidget.value
        auto_gen["rotate_step"] = rotStepWidget.value

    if contrastCheckBox.value:
        auto_gen["is_contrast"] = True
        auto_gen["contrast_min"] = contrastMinWidget.value
        auto_gen["contrast_max"] = contrastMaxWidget.value
        auto_gen["contrast_step"] = contrastStepWidget.value

    if noiseCheckBox.value:
        auto_gen["is_noise"] = True
        auto_gen["noise_max"] = noiseMaxWidget.value
        auto_gen["noise_step"] = noiseStepWidget.value

    if blurCheckBox.value:
        auto_gen["is_blur"] = True
        auto_gen["blur_max"] = blurMaxWidget.value
        auto_gen["blur_step"] = blurStepWidget.value

    jso = {}
    jso["augmen"] = auto_gen
    jso["batch"] = batchSize.value
    jso["continue_custom"] = False
    jso["continue_defalut"] = True
    jso["continue_train"] = True
    jso["custom_wg"] = ""
    jso["gen_jpg"] = True
    jso["gen_path"] = "/tmp/classiftrain_gen"
    jso["gen_png"] = False
    jso["gen_size"] = 608
    jso["keep_aspect_ratio"] = True
    jso["model"] = modelDropdown.value
    jso["prj_path"] = fcImgFolder.selected
    jso["subdivisions"] = subDivisions.value
    jso["unknown_classes"] =0
    jso["use_augmen"] = True
    jso["use_class_balancing"] = True
    jso["use_random_class"] = False

    with open("/tmp/classiftrain.json", "w+") as f:
        f.write(json.dumps(jso, indent=2))

    timer = RepeatTimer(1, callTimerGen)
    timer.start()
    subprocess.call(
        [
            "bash",
            "-c",
            "source /opt/ros/melodic/setup.bash && source /root/install/setup.bash && export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib && /root/install/lib/cira_colab_classiftrain/cira_colab_classiftrain_run gen --platform offscreen",
        ]
    )
    timer.cancel()
    jso = readLogGen()
    genProgress.value = jso["gen_progress"]
    genProgressLabel.value = str(jso["gen_progress"]) + "%"
    btGenFile.disabled = False


btGenFile = Button(description="Generate", button_style="primary")
btGenFile.on_click(onGenerateClicked)
btGenFile.style.font_weight = "bold"
btGenFile.layout.height = "28px"
btGenFile.layout.margin = "6px 10px 0 0"

genProgress = IntProgress(
    value=30,
    min=0,
    max=100,
    bar_style="info",  # 'success', 'info', 'warning', 'danger' or ''
    style={"bar_color": "#1ec693"},
    orientation="horizontal",
)
genProgress.layout.height = "36px"

genProgressLabel = Label("30%")
genProgressLabel.layout.margin = "6px 0 0 6px"

genTrainingFilesBox = Box(
    [
        HTML("<h3 class='text-lg font-bold'>● Generate Training Files</h3>"),
        VBox(
            [
                Box([modelDropdown, batchSize, subDivisions], layout=wrapLayout),
                HBox([btGenFile, genProgress, genProgressLabel]),
                labelWarning,
            ],
            layout=Layout(display="flex", flex_flow="column", grid_gap="10px", padding="0 0 0 10px")
        ),
    ],
    layout=flexCol,
)

genTrainingGroup = VBox([genTrainingFilesBox])


# In[44]:


# @title Training

btTrain = Button(description="Train")
btTrain.add_class("my-button")
btTrain.add_class("bt-train")

accuracy = -1
is_btExport_enable = False


def readLogTrain():
    global accuracy, is_btExport_enable

    jso = {}
    jso["avg"] = -1
    jso["backend"] = "Starting..."
    jso["intr"] = 0
    jso["acc"] = 0
    jso["time_sec"] = 0
    jso["time_str"] = "--:--:--"
    if os.path.exists("/tmp/classiftrain.log"):
        with open("/tmp/classiftrain.log", "r") as f:
            data = f.read()
            if data != "":
                tmp_jso = json.loads(data)["train_state"]
                if tmp_jso["backend"] == "CPU":
                    tmp_jso[
                        "backend"
                    ] = "Training - CPU !!Please change runtime type to GPU"
                else:
                    tmp_jso["backend"] = "Training - " + tmp_jso["backend"]
                jso = tmp_jso

    accuracy = jso["acc"]

    if jso["intr"] > 110 and not is_btExport_enable:
        setEnabled("bt-export", True)
        is_btExport_enable = True

    return jso


if isColab:
    def callTimerTrain():
        jso = readLogTrain()
        return JSON(jso)
    output.register_callback('callTimerTrain', callTimerTrain)
else:
    def callTimerTrain(comm, data):
        jso = readLogTrain()
        return jso
    setup_comm_jupyter("callTimerTrain", callTimerTrain)


def onTrainClicked(p):
    global is_btExport_enable

    if os.path.exists("/tmp/classiftrain.log"):
        os.remove("/tmp/classiftrain.log")

    if os.path.exists("/tmp/classiftrain_gen/data_gen/backup/train.backup"):
        os.remove("/tmp/classiftrain_gen/data_gen/backup/train.backup")

    btTrain.disabled = True
    subprocess.Popen(
        [
            "bash",
            "-c",
            "source /opt/ros/melodic/setup.bash && source /root/install/setup.bash && export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib && /root/install/lib/cira_colab_classiftrain/cira_colab_classiftrain_run train --platform offscreen",
        ]
    )
    is_btExport_enable = False
    setEnabled('bt-export', False)
    callFunc("start()")
    btTrainStop.disabled = False


btTrain.on_click(onTrainClicked)

btTrainStop = Button(description="Stop")
btTrainStop.add_class("my-button")
btTrainStop.add_class("bt-stop")
btTrainStop.disabled = True


def onTrainStopClicked(p):
    btTrain.disabled = False
    btTrainStop.disabled = True
    f = open("/tmp/classiftrain.stop", "w")
    f.write("stop")
    f.close()
    callFunc("stop()")


btTrainStop.on_click(onTrainStopClicked)

btExport = HTML(
    """<button type="button" id="bt-export" onclick="onExportClicked()"
    class="px-6 bg-purple-400 text-gray-800 font-bold rounded shadow-md enabled:hover:bg-purple-500 enabled:hover:shadow-lg enabled:active:bg-purple-600 enabled:active:shadow-lg disabled:opacity-50" 
    disabled>Export</button>"""
)


def exportClicked():
    global accuracy

    if not os.path.exists("/tmp/classiftrain_gen/data_gen/backup/train.backup"):
        return

    setEnabled('bt-export', False)

    export_filename = (
        datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S") + "_" + f"{accuracy:.1f}"
    )
    tmp_file = f"/tmp/{export_filename}.zip"

    if os.path.exists("/content/drive__"):
        tmp_file = "/content/drive/MyDrive/cira_colab_export.zip"

    if os.path.exists(tmp_file):
        os.remove(tmp_file)

    with zipfile.ZipFile(tmp_file, mode="w") as archive:
        archive.write(
            "/tmp/classiftrain_gen/data_gen/names.list",
            arcname=f"{export_filename}/names.list",
        )
        archive.write(
            "/tmp/classiftrain_gen/data_gen/test.cfg",
            arcname=f"{export_filename}/test.cfg",
        )
        archive.write(
            "/tmp/classiftrain_gen/data_gen/backup/train.backup",
            arcname=f"{export_filename}/train.weights",
        )

    if not os.path.exists("/content/drive__"):
        if isColab :
            files.download(tmp_file)
            time.sleep(10)
        else :
            if not os.path.exists("/opt/colab/export"):
                os.makedirs("/opt/colab/export")
            shutil.move(tmp_file, "/opt/colab/export/" + export_filename + ".zip")
            callFunc(f"downloadFile('{export_filename}.zip')")
    else:
        time.sleep(5)
        fid = subprocess.getoutput(
            "xattr -p 'user.drive.id' '/content/drive/MyDrive/cira_colab_export.zip' "
        )

        if isColab:
            output.eval_js(
              f"""
            const anchor = document.createElement('a');
            anchor.href = 'https://drive.google.com/u/0/uc?id={fid}&export=download';
            anchor.download = '{export_filename}.zip';
            anchor.click();
            """
            )
        else:
            pass
        
        time.sleep(5)

    setEnabled('bt-export', True)


if isColab:
    def onExportClicked():
        exportClicked()
    output.register_callback('onExportClicked', onExportClicked)
else:
    def onExportClicked(comm, data):
        exportClicked()
        return {}
    setup_comm_jupyter("onExportClicked", onExportClicked)

trainingJS = Javascript("""
var timer, timerCount;
var timeStart;
var isRunning = false;

function mUpdateTimer(result) {
  document.getElementById("avg-loss").innerHTML = result.avg;
  document.getElementById("accuracy").innerHTML = result.acc.toFixed(1) + '%';
  document.getElementById("iteration").innerHTML = result.intr;
  if (isRunning) {
    document.getElementById("backend").innerHTML = result.backend;
  }
}
if (!isColab) {
    var updateTimerApi = newApi("callTimerTrain", (ret) => {
        mUpdateTimer(ret);
    })
}
async function updateTimer() {
  if (isColab) {
      const res = await google.colab.kernel.invokeFunction('callTimerTrain', [], {});
      const result = res.data['application/json'];
      mUpdateTimer(result);
  } else {
      updateTimerApi.send({});
  }
}

function countTime() {
  elapsTime = Date.now() - timeStart;
  document.getElementById("time").innerHTML = msToHMS(elapsTime);
}

function start() {
  document.getElementById("time").innerHTML = "--:--:--";
  timeStart = Date.now()
  isRunning = true;
  timer = setInterval(updateTimer, 1000);
  timerCount = setInterval(countTime, 1000);
}

function stop() {
  clearInterval(timer);
  clearInterval(timerCount);
  isRunning = false;
  document.getElementById("backend").innerHTML = 'Training - Stop';
}

function msToHMS( duration ) {
     var milliseconds = parseInt((duration % 1000) / 100),
        seconds = parseInt((duration / 1000) % 60),
        minutes = parseInt((duration / (1000 * 60)) % 60),
        hours = parseInt((duration / (1000 * 60 * 60)) % 24);

      hours = (hours < 10) ? "0" + hours : hours;
      minutes = (minutes < 10) ? "0" + minutes : minutes;
      seconds = (seconds < 10) ? "0" + seconds : seconds;

      return hours + ":" + minutes + ":" + seconds ;
}

if (!isColab) {
    var exportClicked = newApi("onExportClicked", (ret) => {
        
    })
}
function onExportClicked() {
  if (isColab) {
      google.colab.kernel.invokeFunction('onExportClicked', [], {});
  } else {
      exportClicked.send({});
  }
}
""")
js.data += trainingJS.data;

checkStop = Checkbox(value=False, description="Stop")

trainingGroup = Box(
    [
        HTML("<h3 class='text-lg font-bold'>● Train</h3>"),
        VBox(
            [
                HBox(
                    [
                        VBox(
                            [
                                HBox(
                                    [btTrain, btTrainStop],
                                    layout=Layout(grid_gap="10px"),
                                ),
                                btExport,
                            ],
                            layout=Layout(
                                display="flex", flex_flow="column", grid_gap="10px"
                            ),
                        ),
                        VBox(
                            [
                                HTML(
                                    """
                                <h2 class='text-xl' id='backend'>---</h2>
                                <h1 class='text-xl'>avg loss: <span id='avg-loss'>-</span></h1>
                                <h2 class='text-3xl'>Accuracy: <span id='accuracy'>-</span></h2>
                                <h2 class='text-xl'>iteration: <span id='iteration'>-</span></h2>
                                <h2 class='text-xl' id='time'>--:--:--</h2>
                                """
                                ),
                            ]
                        ),
                    ],
                    layout=Layout(display="flex", grid_gap="10px"),
                ),
            ],
            layout=Layout(display="flex", padding="0 0 0 10px"),
        ),
    ],
    layout=Layout(display="flex", flex_flow="column", padding="0"),
)


# In[45]:


# @title Testset
fcTestImgFolder = FileChooser("/content")
fcTestImgFolder.title = "<b>Test Image Folder:</b>"
fcTestImgFolder.show_only_dirs = True
fcTestImgFolder.layout.max_height = "250px"

imgList = []


def getImageTestset():
    if fcTestImgFolder.selected is not None:
        image.value = b""
        imgList.clear()
        d = pathlib.Path(fcTestImgFolder.selected)
        for entry in d.iterdir():
            if entry.is_file():
                imgList.append(entry.name)
        imgList.sort()


def handleTestFcImgPath(chooser: FileChooser):
    getImageTestset()
    if len(imgList) > 0:
        callFunc(f"setTestImageList({imgList})")


fcTestImgFolder.register_callback(handleTestFcImgPath)


if isColab:
    def onReloadTestset():
        getImageTestset()
        return JSON(imgList)
    output.register_callback('onReloadTestset', onReloadTestset)
else:
    def onReloadTestset(comm, data):
        getImageTestset()
        return {"data": imgList}
    setup_comm_jupyter("onReloadTestset", onReloadTestset)

testsetJS = Javascript(
    """
if (!isColab) {
    var reloadTestSet = newApi("onReloadTestset", (ret) => {
        setTestImageList(ret.data);
    })
}
async function onReloadTestset() {
  if (isColab) {
      const res = await google.colab.kernel.invokeFunction('onReloadTestset', [], {});
      const result = res.data['application/json'];
      setTestImageList(result);
  } else {
      reloadTestSet.send({});
  }
}
"""
)

js.data += testsetJS.data

btReloadTestset = HTML(
    """<button id="bt-reload-model" onclick="onReloadTestset()"
    class="px-6 my-2 bg-blue-100 text-gray-800 font-bold rounded shadow-md enabled:hover:bg-blue-200 enabled:hover:shadow-lg enabled:active:bg-blue-300 enabled:active:shadow-lg disabled:opacity-50"
    >Reload</button>"""
)

testsetGroup = Box(
    [
        HTML("<h3 class='text-lg font-bold'>● Data test</h3>"),
        fcTestImgFolder,
        btReloadTestset,
    ],
    layout=Layout(display="flex", flex_flow="column", padding="0"),
)


# In[46]:


# @title Testing
btUpdateModel = HTML(
    """<button id="bt-update-model" onclick="onUpdateModel()"
    class="whitespace-nowrap px-6 bg-blue-100 text-gray-800 font-bold rounded shadow-md enabled:hover:bg-blue-200 enabled:hover:shadow-lg enabled:active:bg-blue-300 enabled:active:shadow-lg disabled:opacity-50"
    >Update model</button>"""
)

btPrev = HTML(
    """<button id="bt-prev" onclick="prev()"
    class="whitespace-nowrap px-6 bg-purple-400 text-gray-800 font-bold rounded shadow-md enabled:hover:bg-purple-500 enabled:hover:shadow-lg enabled:active:bg-purple-600 enabled:active:shadow-lg disabled:opacity-50" 
    disabled>< Prev</button>"""
)
btNext = HTML(
    """<button id="bt-next" onclick="next()"
    class="whitespace-nowrap px-6 bg-purple-400 text-gray-800 font-bold rounded shadow-md enabled:hover:bg-purple-500 enabled:hover:shadow-lg enabled:active:bg-purple-600 enabled:active:shadow-lg disabled:opacity-50" 
    disabled>Next ></button>"""
)


def updateModel():
    train_data = {}
    train_data["acc"] = "- (try again)"
    train_data["intr"] = "-"
    if not os.path.exists("/tmp/classiftrain_gen/data_gen/backup/train.backup"):
        return JSON(train_data)

    shutil.copyfile(
        "/tmp/classiftrain_gen/data_gen/names.list",
        "/tmp/deepclassif_model_test/name.list",
    )
    shutil.copyfile(
        "/tmp/classiftrain_gen/data_gen/test.cfg",
        "/tmp/deepclassif_model_test/test.cfg",
    )
    shutil.copyfile(
        "/tmp/classiftrain_gen/data_gen/backup/train.backup",
        "/tmp/deepclassif_model_test/train.weights",
    )
    subprocess.call(["bash", "-c", "echo update > /tmp/deepclassif_test.cmd"])

    timeout_cnt = 50
    cnt = 0

    while not os.path.exists("/tmp/deepclassif.log") and cnt < timeout_cnt:
        time.sleep(0.1)
        cnt = cnt + 1

    log = {}
    with open("/tmp/deepclassif.log") as json_file:
        log = json.load(json_file)

    timeout_cnt = 25
    cnt = 0
    while log["state"] == "update_start" and cnt < timeout_cnt:
        with open("/tmp/deepclassif.log") as json_file:
            log = json.load(json_file)
        time.sleep(0.1)
        cnt = cnt + 1

    if log["state"] == "update_end":
        with open("/tmp/classiftrain.log", "r") as f:
            train_data = json.load(f)["train_state"]
            train_data["acc"] = str(train_data["acc"]) + "%"

    return train_data

if isColab:
    def onUpdateModel():
        train_data = updateModel()
        return JSON(train_data)
    output.register_callback('onUpdateModel', onUpdateModel)
else:
    def onUpdateModel(comm, data):
        train_data = updateModel()
        return train_data
    setup_comm_jupyter("onUpdateModel", onUpdateModel)


def updateImage(imgName):
    if fcTestImgFolder.selected is not None and os.path.exists(
        f"{fcTestImgFolder.selected}{imgName}"
    ):
        imgPath = f"{fcTestImgFolder.selected}{imgName}"

        if os.path.exists("/tmp/deepclassif_result.png"):
            os.remove("/tmp/deepclassif_result.png")
        if os.path.exists("/tmp/deepclassif.log"):
            os.remove("/tmp/deepclassif.log")

        subprocess.call(
            ["bash", "-c", f'echo "test,{imgPath}" > /tmp/deepclassif_test.cmd']
        )

        while not os.path.exists("/tmp/deepclassif.log"):
            time.sleep(0.1)

        log = {}
        log["state"] = "test_start"
        if os.path.exists("/tmp/deepclassif.log"):
            timeout_cnt = 25
            cnt = 0
            with open("/tmp/deepclassif.log") as json_file:
                log = json.load(json_file)
            while (
                log["state"] != "test_error"
                and log["state"] != "test_end"
                and cnt < timeout_cnt
            ):
                with open("/tmp/deepclassif.log") as json_file:
                    log = json.load(json_file)
                time.sleep(0.05)
                cnt = cnt + 1

            if log["state"] == "test_end":
                if os.path.exists("/tmp/deepclassif_result.png"):
                    imgPath = "/tmp/deepclassif_result.png"

        with open(imgPath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            image.value = (
                f'<img src="data:image/png;base64,{encoded_string}" class="h-full" />'
            )

        # with open(imgPath, "rb") as f:
        #   img = f.read()
        #   image.value = img
        #   image.format = pathlib.Path(imgPath).suffix


if isColab:
    def onUpdateImage(imgName):
        updateImage(imgName)
    output.register_callback('onUpdateImage', onUpdateImage)
else:
    def onUpdateImage(comm, data):
        updateImage(data['imgName'])
        return data
    setup_comm_jupyter("onUpdateImage", onUpdateImage)

testingJS = Javascript(
    """
var imgList;
var currImg = -1;
var isLoading = false;
var isUpdateModel = false;

if (!isColab) {
    var updateImagePrevApi = newApi("onUpdateImage", (result) => {
        showImage();
        if (currImg == imgList.length - 2) {
            document.getElementById('bt-next').disabled = false;
        }
        isLoading = false;
    })
}
async function prev() {
  if (isLoading) {
    return;
  }
  isLoading = true;
  currImg--;
  if (currImg == 0) {
    document.getElementById('bt-prev').disabled = true;
    currImg = 0;
  }
  document.getElementById('lb-loading').classList.remove('hidden');
  if (isColab) {
      await google.colab.kernel.invokeFunction('onUpdateImage', [imgList[currImg]], {});
      showImage();
      if (currImg == imgList.length - 2) {
        document.getElementById('bt-next').disabled = false;
      }
      isLoading = false;
  } else {
      updateImagePrevApi.send({'imgName': imgList[currImg]});
  }
}

if (!isColab) {
    var updateImageNextApi = newApi("onUpdateImage", (result) => {
        showImage();
        if (currImg == 1) {
            document.getElementById('bt-prev').disabled = false;
        }
        isLoading = false;
    })
}
async function next() {
  if (isLoading) {
    return;
  }
  isLoading = true;
  currImg++;
  if (currImg == imgList.length - 1) {
    document.getElementById('bt-next').disabled = true;
    currImg = imgList.length - 1;
  }
  document.getElementById('lb-loading').classList.remove('hidden');
    if (isColab) {
      await google.colab.kernel.invokeFunction('onUpdateImage', [imgList[currImg]], {});
      showImage();
      if (currImg == 1) {
        document.getElementById('bt-prev').disabled = false;
      }
      isLoading = false;
    } else {
        updateImageNextApi.send({'imgName': imgList[currImg]});
    }
}

function showImage() {
  document.getElementById('lb-loading').classList.add('hidden')
  document.getElementById('img-file-name').innerHTML = imgList[currImg];
  document.getElementById('lb').innerHTML = (currImg + 1) + ' / ' + imgList.length;
}

if (!isColab) {
    var updateModelApi = newApi("onUpdateModel", (result) => {
        if (result.hasOwnProperty('acc')) {
            document.getElementById('lb-model-avg-loss').innerHTML = 'Accuracy : ' + result.acc;
        }
        if (result.hasOwnProperty('intr')) {
            document.getElementById('lb-model-iteration').innerHTML = 'Iteration: ' + result.intr;
        }
        isUpdateModel = false;
        document.getElementById('bt-update-model').disabled = false;
    })
}
async function onUpdateModel() {
  if (isUpdateModel) {
    return;
  }
  isUpdateModel = true;
  document.getElementById('bt-update-model').disabled = true;
  if (isColab) {
    const res = await google.colab.kernel.invokeFunction('onUpdateModel', [], {});
    const result = res.data['application/json'];
    if (result.hasOwnProperty('acc')) {
    document.getElementById('lb-model-avg-loss').innerHTML = 'Accuracy : ' + result.acc;
    }
    if (result.hasOwnProperty('intr')) {
    document.getElementById('lb-model-iteration').innerHTML = 'Iteration: ' + result.intr;
    }
    isUpdateModel = false;
    document.getElementById('bt-update-model').disabled = false;
  } else {
    updateModelApi.send({});
  }
}

function setTestImageList(imgPathList) {
  if (imgPathList.length > 0) {
    imgList = imgPathList;
    document.getElementById('lb').innerHTML = '0 / ' + imgList.length;
    currImg = -1;
    document.getElementById('bt-next').disabled = false;
    document.getElementById('img-file-name').innerHTML = '-';
  }
}
"""
)
js.data += testingJS.data

# image = Image()
# image.layout.max_width = '608px'
# image.layout.max_height = '608px'
image = HTML('<img src="data:image/png;base64," />')
image.layout.height = "304px"

runningGroup = Box(
    [
        HTML("<h3 class='text-lg font-bold'>● Run test</h3>"),
        HBox(
            [
                btUpdateModel,
                HTML(
                    "<div id='lb-model' class='w-48 h-full flex flex-col text-sm self-center'><p id='lb-model-avg-loss' class='text-lg'>Accuracy: -</p><p id='lb-model-iteration' class='text-lg'>Iteration: -</p></div>"
                ),
                btPrev,
                btNext,
                HTML("<div class='whitespace-nowrap px-8' id='lb'>0 / 0</div>"),
                HTML(
                    """<div class="w-7" role="status">
    <svg id="lb-loading" class="hidden w-7 h-7 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/>
        <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/>
    </svg>
</div>"""
                ),
                HTML('<h1 id="img-file-name" class="whitespace-nowrap text-md">-</h1>'),
            ],
            layout=Layout(grid_gap="10px", margin="0 0 2px 0"),
        ),
        image,
    ],
    layout=Layout(display="flex", flex_flow="column"),
)


# In[47]:


#@title Style
style = """
<style>
body {
  margin: 0;
  padding: 0;
}
.widget-box .widget-label {
  width: 100px;
}
.p-Collapse-header,
.p-Collapse-open > .p-Collapse-header {
  padding: 10px 8px;
  font-size: 18px;
  color: var(--colab-primary-text-color);
}
.p-Collapse-open > .p-Collapse-header:hover {
  cursor: pointer;
}
.p-Collapse-contents {
  padding: 0px 10px 4px 10px;
}
.jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tabLabel {
  color: var(--colab-primary-text-color);
  font-size: 16px;
  text-align: center;
}
.jupyter-widgets.widget-tab > .p-TabBar .p-TabBar-tab {
  padding: 3px;
}
.jupyter-widgets.widget-tab > .widget-tab-contents {
  padding: 0 4px;
}
.my-button {
  font-weight: bold;
  border-radius: 5px;
  width: fit-content;
  padding: 0 20px;
  cursor: pointer;
}
.bt-train {
  color: #424242;
  background-color: #86e055;
  outline: none;
  border: none;
}
.bt-train:hover {
  opacity: 0.8;
}
.bt-train:disabled {
  cursor: progress;
}
.bt-stop {
  color: #424242;
  background-color: #ed4747;
  outline: none;
}
.bt-stop:hover {
  opacity: 0.8;
}
.bt-stop:disabled {
  cursor: not-allowed;
}
.bt-export {
  color: #424242;
  background-color: #ed4747;
  outline: none;
}
.bt-export:hover {
  opacity: 0.8;
}
.bt-export:disabled {
  cursor: not-allowed;
}
</style>
"""


# In[48]:


#@title JS
mainJS = Javascript("""
if (!isColab) {
    Jupyter.notebook.kernel.comm_manager.register_target('evalJS',
    (comm, msg) => {
        comm.on_msg((msg) => {
            eval(msg.content.data);
        });
    });
}
function setEnabled(eid, enable) {
  document.getElementById(eid).disabled = !enable;
}
function downloadFile(filename) {
    const anchor = document.createElement('a');
    anchor.href = window.location.origin + '/files/export/' + filename;
    anchor.download = filename;
    anchor.click();
}
""")
js.data += mainJS.data;


# In[49]:


# @title Display
genProgress.value = 0
genProgressLabel.value = "0%"

trainingGroup.layout.min_width = '500px'

tab = Tab(children=[VBox([datasetGroup, augmentConfigGroup, genTrainingGroup]), VBox([HBox([trainingGroup, testsetGroup], layout=wrapLayout), HTML('<div class="w-full h-0.5 bg-gray-300 rounded"></div>'), runningGroup])])
tab.set_title(0, "DataGen")
tab.set_title(1, "Train&Test")
tab.selected_index = 0

time.sleep(3)

colabCount = "-"
with open("/tmp/classiftrain_colab.count", "r") as f:
    colabCount = f.read()

display(
    dHTML('''
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    '''),
    HTML(style),
    dHTML(f"""<script type="text/javascript">{js.data}</script>"""),
    HTML(f"""
    <div class='flex items-end gap-4 mb-1'>
      <img src='https://raw.githubusercontent.com/CiRA-AMI/cira-colab-trainer/main/cira_classiftrain_colab_50.png' width='143px' height='79px' />
      <h1 class='text-2xl font-bold'>CiRA ClassifTrain Colab</h1>
      <h1>Visitor: {colabCount}</h1>
    </div>"""),
    tab,
)

image.value = '<img src="data:image/png;base64," />'
if isColab:
    def setEnabled(eid, enable):
        output.eval_js(f"setEnabled('{eid}', {'true' if enable else 'false'})")
    def callFunc(func):
        output.eval_js(func)
    output.eval_js(f"setTestImageList({imgList})")
else:
    from ipykernel.comm import Comm
    def setEnabled(eid, enable):
        evalJS.send(f"""setEnabled('{eid}', {"true" if enable else "false"})""")
    def callFunc(func):
        evalJS.send(func)
    evalJS = Comm(target_name='evalJS')
    evalJS.send(f"setTestImageList({imgList})")


# In[ ]:




