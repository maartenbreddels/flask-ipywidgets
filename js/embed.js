
import { DefaultKernel, Kernel, ServerConnection, KernelMessage } from '@jupyterlab/services'

import { OutputAreaModel, OutputArea } from '@jupyterlab/outputarea';

import { WidgetManager } from './manager'
import { renderMime } from './renderMime'
//import * as htmlmanager from '@jupyter-widgets/html-manager/libembed'

import 'font-awesome/css/font-awesome.css'
import './widgets.css'


var requirePromise = function(pkg) {
    return new Promise((resolve, reject) => {
        let require = window.require;
        if (require === undefined) {
            reject("Requirejs is needed, please ensure it is loaded on the page.");
        } else {
            require(pkg, resolve, reject);
        }
    });
}

function requireLoader(moduleName, moduleVersion) {
    return requirePromise([`${moduleName}`]).catch((err) => {
        let failedId = err.requireModules && err.requireModules[0];
        if (failedId) {
            console.log(`Falling back to unpkg.com for ${moduleName}@${moduleVersion}`);
            return requirePromise([`https://unpkg.com/${moduleName}@${moduleVersion}/dist/index.js`]);
        }
    });
}
function renderEmbeddedWidgets(element = document.documentElement) {
    requirePromise(['@jupyter-widgets/html-manager']).then((htmlmanager) => {
        let managerFactory = () => {
            return new htmlmanager.HTMLManager({loader: requireLoader});
        }
        libembed.renderWidgets(managerFactory, element);
    });
}

function renderManager(element, widgetState, managerFactory) {
    let valid = true; //model_validate(widgetState);
    if (!valid) {
        console.error('Model state has errors.', model_validate.errors);
    }
    let manager = managerFactory();
    manager.set_state(widgetState).then(function(models) {
        let tags = element.querySelectorAll('script[type="application/vnd.jupyter.widget-view+json"]');
        for (let i=0; i!=tags.length; ++i) {
            let viewtag = tags[i];
            let widgetViewObject = JSON.parse(viewtag.innerHTML);
            let valid = true; //view_validate(widgetViewObject);
            if (!valid) {
                console.error('View state has errors.', view_validate.errors);
            }
            let model_id = widgetViewObject.model_id;
            // Find the model id in the models. We should use .find, but IE
            // doesn't support .find
            let model = models.filter( (item) => {
                return item.model_id == model_id;
            })[0];
            if (model !== undefined) {
                let prev = viewtag.previousElementSibling;
                if (prev && prev.tagName === 'img' && prev.classList.contains('jupyter-widget')) {
                    viewtag.parentElement.removeChild(prev);
                }
                let widgetTag = document.createElement('div');
                widgetTag.className = 'widget-subarea';
                viewtag.parentElement.insertBefore(widgetTag, viewtag);
                manager.display_model(undefined, model, { el : widgetTag });
            }
        }
    });
}

export async function renderWidgets(baseUrl, wsUrl, loader) {
    baseUrl = '/jupyter';
    wsUrl += '/jupyter'

    let connectionInfo = ServerConnection.makeSettings({
        baseUrl,
        wsUrl
    });

    const kernelSpecs = await Kernel.getSpecs(connectionInfo)

    console.log(`Starting kernel ${kernelSpecs.default}`)

    const kernel = await Kernel.startNew({
        name: kernelSpecs.default,
        serverSettings: connectionInfo
    });

    const el = document.getElementById('ipywidget-server-result')
    const errorEl = document.getElementById('ipywidget-server-errors')
    const manager = new WidgetManager(kernel, el, loader);
    const outputModel = new OutputAreaModel({trusted: true});
    const outputView = new OutputArea({
        rendermime: renderMime,
        model: outputModel,
    })
    errorEl.appendChild(outputView.node)

    const options = {
        msgType: 'custom_message',
        channel: 'shell'
    }
    const msg = KernelMessage.createShellMessage(options)
    const execution = kernel.sendShellMessage(msg, true)
    window.manager = manager


    //*
    var element = document.documentElement;
    var tags = element.querySelectorAll('script[type="application/vnd.jupyter.widget-state+json"]');
    for (var i = 0; i != tags.length; ++i) {
        renderManager(element, JSON.parse(tags[i].innerHTML), () => manager);
    }/**/
    //htmlmanager.renderWidgets(() => manager)


    execution.onIOPub = (msg) => {
        // If we have a display message, display the widget.
        if (KernelMessage.isDisplayDataMsg(msg)) {
            let widgetData = msg.content.data['application/vnd.jupyter.widget-view+json'];
            if (widgetData !== undefined && widgetData.version_major === 2) {
                let model = manager.get_model(widgetData.model_id);
                if (model !== undefined) {
                    model.then(model => {
                        manager.display_model(msg, model);
                    });
                }
            }
        }
        else if (KernelMessage.isErrorMsg(msg)) {
            // Show errors to help with debugging
            const model = msg.content
            model.output_type = 'error'
            outputModel.add(model)
        }
    }/**/
}
