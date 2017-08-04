import pyblish.api
import os
import pymel
import pymel.core as pm

@pyblish.api.log
class ExtractDeadlineLayer(pyblish.api.InstancePlugin):
    """ Gathers optional Maya related data for Deadline
    """

    order = pyblish.api.ExtractorOrder + 0.3
    hosts = ['maya']
    families = ['deadline']
    label = 'Layer to Deadline'

    def process(self, instance):

        # getting deadline data
        job_data = {}
        plugin_data = {}
        if instance.has_data('deadlineData'):
            job_data = instance.data('deadlineData')['job'].copy()
            plugin_data = instance.data['deadlineData']['plugin'].copy()
        else:
            instance.data['deadlineData'] = {}

        current_file = instance.context.data('currentFile')
        directory, filename = os.path.split(str(current_file))

        hostversion = pymel.versions.fullName()
        build = pymel.versions.bitness()

        if 'ass.farm' in instance.data['families']:
            self.log.info('ASS export on the farm are not yet supported')
        elif 'ass.local' in instance.data['families']:
            job_data['Plugin'] = 'Arnold'
            job_data['group'] = 'arnold'
            job_data['LimitGroups'] = instance.data['renderer']
            plugin_data['InputFile'] = instance.data['publishFile']
            plugin_data['LocalRendering'] = 'False'
            mtoa_version = pymel.core.pluginInfo('mtoa', query=True, version=True)
            plugin_data['Executable'] = 'mtoa_' + hostversion + '_' + mtoa_version

            mtoa_path = pm.pluginInfo('mtoa', query=True, path=True)
            PluginFolder1 = os.path.split(mtoa_path)[0].replace('plug-ins', 'shaders')
            plugin_data['PluginFolder1'] = PluginFolder1

            PluginFolder2 = ''
            if mtoa_version.startswith("1.4"):
                PluginFolder2 = '\\\\kre-c01\\share\\core\\software\\arnold\\alShaders-win-1.0.0rc18-ai4.2.12.2\\bin'
            plugin_data['PluginFolder2'] = PluginFolder2

            PluginFolder2 = ''
            if mtoa_version.startswith("2."):
                PluginFolder2 = '\\\\kre-c01\\share\\core\\software\\arnold\\alShaders-win-2.0.0-ai5.0.1.0\\bin'
            plugin_data['PluginFolder2'] = PluginFolder2

            PluginFolder3 = ''
            if pm.pluginInfo( 'pgYetiMaya', query=True, loaded=True):
                yeti_path = pm.pluginInfo('pgYetiMaya', query=True, path=True)
                PluginFolder3 = os.path.split(yeti_path)[0].replace('plug-ins', 'bin')
            plugin_data['PluginFolder3'] = PluginFolder3

            plugin_data['PathFolder1'] = PluginFolder3

            plugin_data['Version'] = 'Beta'
            plugin_data['CommandLineOptions'] = ''
            plugin_data['Verbose'] = '4'
        else:
            job_data['Plugin'] = 'MayaBatch'
            job_data['LimitGroups'] = instance.data['renderer']
            job_data['Group'] = 'maya_' + hostversion.replace('.', '_')
            plugin_data['SceneFile'] = instance.context.data['publishFile']
            plugin_data['ProjectPath'] = instance.data['projectPath']
            plugin_data['Version'] = hostversion
            plugin_data['Build'] = build
            plugin_data['Renderer'] = instance.data['renderer']
            plugin_data['UsingRenderLayers'] = '1'
            plugin_data['RenderLayer'] = instance.name

        job_data['Name'] = filename + " - " + instance.name
        job_data['UserName'] = instance.context.data['user']
        job_data['Pool'] = 'cg'
        job_data['Frames'] = instance.data['frames']
        job_data['OutputFilename0'] = instance.data['outputFilename']


        instance.data['deadlineData']['job'] = job_data
        instance.data['deadlineData']['plugin'] = plugin_data
