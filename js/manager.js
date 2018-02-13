
import * as base from '@jupyter-widgets/base'
import * as controls from '@jupyter-widgets/controls';
//import * as utils from '@jupyter-widgets/base/utils';
import * as pWidget from '@phosphor/widgets';

import { HTMLManager } from '@jupyter-widgets/html-manager';

import * as outputWidgets from './output';

var utils = base;

export class WidgetManager extends HTMLManager {
    constructor(kernel, el, loader) {
        super();
        this.kernel = kernel;
        this.registerWithKernel(kernel)
        this.el = el;
        this.loader = loader;
        console.log('widget manager')
    }

    registerWithKernel(kernel) {
        if (this._commRegistration) {
            this._commRegistration.dispose();
        }
        this._commRegistration = kernel.registerCommTarget(
            this.comm_target_name,
            (comm, msg) => this.handle_comm_open(new base.shims.services.Comm(comm), msg)
        );
    }

    display_view(msg, view, options) {
        console.log('view', msg, view, options)
        return Promise.resolve(view).then(view => {
            pWidget.Widget.attach(view.pWidget, this.el);
            view.on('remove', function() {
                console.log('view removed', view);
            });
            return view;
        });
    }

    loadClass(className, moduleName, moduleVersion) {
        console.log(className, moduleName)
        if (moduleName === '@jupyter-widgets/output') {
            return Promise.resolve(outputWidgets).then(module => {
                if (module[className]) {
                    return module[className];
                } else {
                    return Promise.reject(
                        `Class ${className} not found in module ${moduleName}`
                    );
                }
            })
        } else {
            return super.loadClass(className, moduleName, moduleVersion)
        }
    }

    _create_comm(target_name, model_id, data, metadata) {
        const comm = this.kernel.connectToComm(target_name, model_id)
        if (data || metadata) {
            comm.open(data, metadata)
        }
        console.log('_create_comm', target_name, model_id)
        return Promise.resolve(new base.shims.services.Comm(comm))
    }

    _old_get_comm_info() {
        return this.kernel.requestCommInfo({ target: this.comm_target_name})
            .then(reply => reply.content.comms)
    }
    set_state(state) {
        this._last_state = state
        //console.log('set state', state)
        //return super.set_state(state)
        var _this = this;
        // Check to make sure that it's the same version we are parsing.
        if (!(state.version_major && state.version_major <= 2)) {
            throw 'Unsupported widget state format';
        }
        var models = state.state;
        // Recreate all the widget models for the given widget manager state.
        var all_models = this._get_comm_info().then(function (live_comms) {
            return Promise.all(Object.keys(models).map(function (model_id) {
                // First put back the binary buffers
                var decode = { 'base64': utils.base64ToBuffer, 'hex': utils.hexToBuffer };
                var model = models[model_id];
                var modelState = model.state;
                if (model.buffers) {
                    var bufferPaths = model.buffers.map(function (b) { return b.path; });
                    // put_buffers expects buffers to be DataViews
                    var buffers = model.buffers.map(function (b) { return new DataView(decode[b.encoding](b.data)); });
                    utils.put_buffers(model.state, bufferPaths, buffers);
                }
                // If the model has already been created, set its state and then
                // return it.
                if (_this._models[model_id]) {
                    return _this._models[model_id].then(function (model) {
                        // deserialize state
                        return model.constructor._deserialize_state(modelState || {}, _this).then(function (attributes) {
                            model.set_state(attributes);
                            return model;
                        });
                    });
                }
                var modelCreate = {
                    model_id: model_id,
                    model_name: model.model_name,
                    model_module: model.model_module,
                    model_module_version: model.model_module_version
                };
                if (live_comms.hasOwnProperty(model_id)) {
                    // This connects to an existing comm if it exists, and
                    // should *not* send a comm open message.
                    return _this._create_comm(_this.comm_target_name, model_id).then(function (comm) {
                        modelCreate.comm = comm;
                        return _this.new_model(modelCreate, modelState);
                    });
                }
                else {
                    return _this.new_model(modelCreate, modelState);
                }
            }));
        });
        return all_models;
    }
    _get_comm_info() {
        return Promise.resolve(this._last_state.state)
    }
}
