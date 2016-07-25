
from PySide import QtXml, QtGui
import os

import data_model as dtm
reload(dtm)

#import modules.data as data
#reload(data)
import modules.files as files
reload(files)
import modules.jsonData as data
reload(data)
import modules.maya_warpper as maya
reload(maya)

global _node_
global _root_
global  _stage_
global _asset_
global _folder_
global _dummy_
global _new_

_new_ = "new"
_node_ = "node"
_root_ = "root"
_stage_ = "stage"
_asset_ = "asset"
_folder_ = "folder" 
_dummy_ = "dummy"
_version_ = "version"


def set_icons():
    localIconPath = os.path.join(os.path.dirname(__file__), 'icons')
    if not os.path.exists(localIconPath):
        return 
        
    global folder_icon
    global cube_icon
    global add_cube_icon
    global dummy_icon
    
    global cube_icon_full
    global add_icon
    global large_image_icon
    folder_icon = os.path.join(localIconPath, "%s.svg"%"folder")
    cube_icon = os.path.join(localIconPath, "%s.svg"%"cube") 
    add_cube_icon = os.path.join(localIconPath, "%s.svg"%"add_cube")     
    cube_icon_full = os.path.join(localIconPath, "%s.svg"%"cube-fill") 
    add_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg"%"add"))
    large_image_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg"%"large_image")) 
    dummy_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg"%"braces")) 
    
    
set_icons()

class Metadata_file(object):
    
    def __init__(self,**kwargs):
        self.data_file = None
        self.data_file_path = None
        
        
        for key in kwargs:
            if key == "path":
                self.data_file_path = kwargs[key]
                
        if self.data_file_path:        
            self.set_data_file(self.data_file_path)


    def set_data_file(self,path): 
        
        if os.path.isfile(path):          
            self.data_file = data.jsonDict(path = path) 
            return True
        else:
            print "invalid path"

class Node(object):
    
    def __init__(self, name,  parent=None):
        
        super(Node, self).__init__()
        
        self._name = name
        self._children = []
        self._parent = parent
        self.expendedState = False
        self._id = data.id_generator()

        if parent is not None:
            parent.addChild(self)


    def attrs(self):

        classes = self.__class__.__mro__

        kv = {}

        for cls in classes:
            for k, v in cls.__dict__.iteritems():
                if isinstance(v, property):
                    #print "Property:", k.rstrip("_"), "\n\tValue:", v.fget(self)
                    kv[k] = v.fget(self)

        return kv

    def asXml(self):
        
        doc = QtXml.QDomDocument()
        

        node = doc.createElement(self.typeInfo())
        doc.appendChild(node)

        attrs = self.attrs().iteritems()
        
        for k, v in attrs:
            node.setAttribute(k, v) 
  
       
        for i in self._children:
            i._recurseXml(doc, node)

        return doc.toString(indent=4)


    def _recurseXml(self, doc, parent):
        node = doc.createElement(self.typeInfo())
        parent.appendChild(node)

        attrs = self.attrs().iteritems()
        
        for k, v in attrs:
            node.setAttribute(k, v)

        for i in self._children:
            i._recurseXml(doc, node)

    
    def typeInfo(self):
        return _node_

    def addChild(self, child):
        self._children.append(child)
        child._parent = self

    def insertChild(self, position, child):
        
        if position < 0 or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        
        if position < 0 or position > len(self._children):
            return False
        
        if self._children != []:
            child = self._children.pop(position)
            #child.delete()
            child._parent = None

            return True
        else:
            return False
            
    @property
    def name(self):
        return self._name
                
    @name.setter
    def name(self, value):
        self._name = value

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent
    
    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)


    def log(self, tabLevel=-1):

        output     = ""
        tabLevel += 1
        
        for i in range(tabLevel):
            output += "\t"
        
        output += "|------" + self._name + "\n"
        
        for child in self._children:
            output += child.log(tabLevel)
        
        tabLevel -= 1
        output += "\n"
        
        return output
      

    def data(self, column):
        
        if   column is 0: return self.name
        elif column is 1: return None
    
    def setData(self, column, value):
        #print value
        if   column is 0: self.name = value
        elif column is 1: pass
    
    def resource(self):
        return folder_icon
        
    def delete(self):

        self.delete_me()
        
        for child in self._children:
            
            child.delete()

    def delete_me(self):
        print "***DELETE ALL IN" + self._name + "\n"
    
    @property
    def expendedState(self):
        return self._expendedState
    @expendedState.setter
    def expendedState(self, state):    
        self._expendedState = state

    @property
    def id(self):
        return self._id


class RootNode(Node, Metadata_file):
    
    def __init__(self, name, parent=None, **kwargs):
        super(RootNode, self).__init__(name, parent)
        
        self.name = name
    
        self._path = None
        for key in kwargs:
            if key == "path":
                self._path = kwargs[key]
        
        
            
    def create(self, path = None):
        if files.create_directory(path):  
            self.path = path          
            return self
        else:
            return False


    @property
    def path(self):
        return self._path
                
    @path.setter
    def path(self, path):
        self._path = path  
    
    def typeInfo(self):
        return _root_
  
    def resource(self):
        return folder_icon

    def model_tree(self):
        
        '''
        returns a flat list of all descending childs from the given index
        '''     
        def rec(path, parent):
            if path:
                folders = files.list_dir_folders(path)
                if folders:
                    for dir in folders: 
                        p  = os.path.join(path,dir)
 
                        if files.assetDir( p ):
                            node = AssetNode(os.path.split(p)[1], path=p, parent = parent) 
                            rec(p, node)
                        elif files.stageDir( p ):
                            node = StageNode(os.path.split(p)[1], stage = dir, path=p, parent = parent)   
                        else:                         
                            node = FolderNode(os.path.split(p)[1], path=p, parent = parent)                        
                            rec(p, node)
                else:
                    pass

        rec(self.path, self)

class FolderNode(RootNode):
    
    def __init__(self, name,  parent=None, **kwargs):
        super(FolderNode, self).__init__(name, parent, **kwargs)
   
       
        
    def typeInfo(self):
        return _folder_
          
    def resource(self):
        return folder_icon


class AssetNode(RootNode):
    
    def __init__(self, name,  parent=None, **kwargs):
        super(AssetNode, self).__init__(name, parent, **kwargs)
      
    def create(self, path = None):
        node = super(AssetNode, self).create(path)
        if node:
            dict = {}
            dict["typeInfo"] = "_asset_"
            
            path = os.path.join(path,"%s.%s"%("asset","json"))
            
            self.data_file = data.jsonDict().create(path, dict)  
            self.data_file = self.data_file.read()
            return node
        
        
    def typeInfo(self):
        return _asset_
          
    def resource(self):
        return cube_icon_full
        
        
class StageNode(RootNode):
    
    def __init__(self, name, stage = None, parent=None, **kwargs):
        super(StageNode, self).__init__(name, parent, **kwargs)
      
        self._stage = stage
        
    def create(self, stage = None, path = None):
        node = super(StageNode, self).create(path)
        if node:
                        
            dict = {}
            dict["typeInfo"] = "_stage_"
            dict["stage"] = stage
            
            self._stage = stage
            
            path = os.path.join(path,"%s.%s"%("stage","json"))
            
            self.data_file = data.jsonDict().create(path, dict)  
            self.data_file = self.data_file.read()
            return node

    @property  
    def stage(self):
        return self._stage
    
    @stage.setter
    def stage(self, value):
        self._stage = value

    def typeInfo(self):
        return _stage_

   
    def resource(self):
        return large_image_icon
                           

class VersionNode(Node):
    
    def __init__(self, name,path = None,  number = None, author = None, date = None, note = None, stage = None, parent=None):
        super(VersionNode, self).__init__(name, parent)
        
        self._path = path
        self._number = number
        self._date = date
        self._note = note
        self._author = author
        self._stage = stage


    @property
    def stage(self):
        return self._stage

    @property
    def number(self):
        return self._number

    @property
    def date(self):
        return self._date

    @property
    def author(self):
        return self._author

    @property
    def note(self):
        return self._note
        
    @note.setter
    def note(self, note):
        self._note = note

    @property
    def path(self):
        return self._path
        
    @path.setter
    def path(self, path):
        self._path = path


    def typeInfo(self):
        return _version_
  
    def resource(self):
        return None  


class DummyNode(Node):
    
    def __init__(self, name, parent=None):
        super(DummyNode, self).__init__(name, parent)


    def typeInfo(self):
        return _dummy_
  
    def resource(self):
        return dummy_icon

class AddNode(Node):
    def __init__(self, name, parent=None):
        super(AddNode, self).__init__(name, parent)

    def typeInfo(self):
        return _new_

    def resource(self):
        return add_icon

class NewNode(Node):

    def __init__(self, name, stage = None, parent=None):
        super(NewNode, self).__init__(name, parent)

        self._stage = stage

    @property
    def stage(self):
        return self._stage

    def typeInfo(self):
        return _new_

    def resource(self):
        return add_icon



class project(object):
    def __init__(self, project_path):

        stages = {}
        stages["asset"] = ["model","rig","clip","shandeing","lightning"]
        stages["animation"] = ["layout","Shot"]   

        levels = {}
        levels["asset"] = ["type","asset","stage","ccc"]
        levels["animation"] = ["Ep","Seq"]

                
        self.project = {}
        self.project["project_path"] = project_path


        self.project["levels"] = levels          
        self.project["stages"] = stages   
        
        self.project["current_stage"] = None
                                
                                



class Asset(Metadata_file):
    def __init__(self,**kwargs):
        Metadata_file.__init__(self, **kwargs)
       
        self.project = None
        for key in kwargs:
            if key == "project":
                self.project = kwargs[key]
        
        
        self.settings = None
        for key in kwargs:
            if key == "settings":
                self.settings = kwargs[key]
                                
    
    
    def create(self, path, name):
        data = {}
        data["typeInfo"] = "_asset_"
        
        path = os.path.join(path,"%s.%s"%(name,"json"))
        
        self.data_file = data.jsonDict().create(path, data)  
        self.data_file = self.data_file.read()
       
        return self
                                
class Stage(Metadata_file):
    def __init__(self,**kwargs):
        Metadata_file.__init__(self, **kwargs)
       
        self.project = None
        for key in kwargs:
            if key == "project":
                self.project = kwargs[key]
        
        
        self.settings = None
        for key in kwargs:
            if key == "settings":
                self.settings = kwargs[key]

        self.pipelineUI = None
        for key in kwargs:
            if key == "pipelineUI":
                self.pipelineUI = kwargs[key]

    

    def create(self):


        files.assure_folder_exists(self.versions_path)


        maya.new_scene()
        maya.set_fps(self.project.project_fps)
        maya.rewind()

        version_number = files.set_padding(1, self.project.project_padding)

        file_name = "%s_%s.%s" % ("fsfafsa", version_number, "ma")

        scene_path = maya.save_scene_as(path=self.versions_path, file_name=file_name)

        #first_version = {}
        #first_version["path"] = scene_path
        #first_version["date_created"] = "%s %s" % (time.strftime("%d/%m/%Y"), time.strftime("%H:%M:%S"))
        #first_version["author"] = self.settings.user[0]
        #first_version["note"] = "No notes"

        #versions = {}
        #versions[version_number] = first_version

        self.pipelineUI.updateVersionsTable()
        return
        '''
        self.project = project
        self.settings = settings
        
        versions_path = os.path.join(path, "versions")       
        masters_path = os.path.join(path, "masters")
        tumbnails_path =  os.path.join(path, "tumbnails") 
        
        for folder_path in [versions_path, masters_path, tumbnails_path]:
            files.create_directory(folder_path)

        if not create_from:
            maya.new_scene()
            maya.set_fps(self.project.project_fps)
            maya.rewind()
            
        elif create_from == "current_scene":
            pass    
            
        version_number = set_padding(1,self.project.project_padding)
        
        file_name = "%s_%s_%s.%s"%(asset_name,component_name,version_number,"ma")    
        
        scene_path = maya.save_scene_as(path = versions_path, file_name = file_name )       
        
        first_version = {}
        first_version["path"] = scene_path
        first_version["date_created"] = "%s %s"%(time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"))
        first_version["author"] = self.settings.user[0]
        first_version["note"] = "No notes"
        
        versions = {}
        versions[version_number] = first_version
        
        masters = {}
                               
        component_data = {}
        component_data["component_name"] = component_name
        component_data["asset_name"] = asset_name
        component_data["catagory_name"] = catagory_name
        component_data["versions"] = versions
        component_data["masters"] = masters
        
        path = os.path.join(path,"%s.%s"%(component_name,"pipe"))           
        self.data_file = data.pickleDict().create(path, component_data)  
        self.data_file = self.data_file.read()
       
        return self
        '''
    @property
    def stage_path(self):
        if self.data_file:
            
            return os.path.dirname(self.data_file_path)
            #
            #if self.settings:            
            #    return os.path.join(self.settings.current_project_path, self.project.assets_dir,self.catagory_name,self.asset_name,self.component_name)  
        else:
            return None  

    @property
    def versions_path(self):
        if self.data_file:
            if self.settings:                             
                return os.path.join(self.stage_path, "versions") 
        else:
            return None  

    @property
    def masters_path(self):
        if self.data_file:
            if self.settings:                             
                return os.path.join(self.stage_path, "masters") 
        else:
            return None  
   

    @property
    def tumbnails_path(self):
        if self.data_file:
            if self.settings:                             
                return os.path.join(self.stage_path, "tumbnails") 
        else:
            return None  

    @property  
    def versions_(self):
        if self.data_file:
            return self.data_file["versions"]
    
    @versions_.setter
    def versions_(self,versions):
       
        if self.data_file:
            data = {}
            data["versions"] = versions
            self.data_file.edit(data)
            self.data_file = self.data_file.read()



    @property  
    def masters_(self):
        if self.data_file:
            return self.data_file["masters"]
    
    @masters_.setter
    def masters_(self,masters):
       
        if self.data_file:
            data = {}
            data["masters"] = masters
            self.data_file.edit(data)
            self.data_file = self.data_file.read()

    @property
    def component_name(self):
        if self.data_file:
            try:
                return self.data_file["component_name"]
            except:
                return None
        else:
            return None  
            
    @component_name.setter
    def component_name(self,name):
        if self.data_file:
            data = {}
            data["component_name"] = name
            self.data_file.edit(data)
            self.data_file = self.data_file.read()
        else:
            return None              

    @property
    def catagory_name(self):
        if self.data_file:
            return self.data_file["catagory_name"]
        else:
            return None  

    @catagory_name.setter
    def catagory_name(self,name):
        if self.data_file:
            data = {}
            data["catagory_name"] = name
            self.data_file.edit(data)
            self.data_file = self.data_file.read()
        else:
            return None 

    @property
    def asset_name(self):
        if self.data_file:
            return self.data_file["asset_name"]
        else:
            return None  



    @asset_name.setter
    def asset_name(self,name):
        if self.data_file:
            data = {}
            data["asset_name"] = name
            self.data_file.edit(data)
            self.data_file = self.data_file.read()
        else:
            return None  


    @property
    def component_public_state(self):
        if self.data_file:
            if "component_public_state" in self.data_file:
                return self.data_file["component_public_state"]
            else:
                # for legacy components, if no public state key exists, then the component is public
                return True
        else:
            return None  
            
    @component_public_state.setter
    def component_public_state(self,state):
        if self.data_file:
            data = {}
            data["component_public_state"] = state
            self.data_file.edit(data)
            self.data_file = self.data_file.read()
        else:
            return None 


    def path(self, type, version):
        if self.data_file:
            try:                
                version_data = self.data_file[type][version]
                return version_data["path"]
            except:
                return None
            
        else:
            return None  

    def author(self, type, version):
        
        if self.data_file:
            try:
                version_data = self.data_file[type][version]
                return version_data["author"]
            except:
                return None

        else:
            return None  


    def date_created(self, type, version):
        if self.data_file:
            try:
                version_data = self.data_file[type][version]
                return version_data["date_created"]
            except:
                return None
            
        else:
            return None  

    def note(self, type, version, **kwargs):
        if self.data_file:
            
            note = None
            for key in kwargs:
                if key == "note":
                    note = kwargs[key]
            
            if note:
                  
                data = self.data_file.read()
                data[type][version]["note"] = note    
                self.data_file.edit(data)
                self.data_file = self.data_file.read()
                
                return True
                                                
            else:
                
                try:
                    version_data = self.data_file[type][version]
                    return version_data["note"]
                except:
                    return None
            
        else:
            return None  
 
    def size(self, type, version):
        
        if self.data_file:            
            size_mb = files.file_size_mb(self.file_path(type, version))
            if size_mb:
                return ("{0:.1f}".format(size_mb))   
            else:
                # maybe this is the master file
                size_mb = files.file_size_mb(self.master)
                if size_mb:
                    return ("{0:.1f}".format(size_mb))     
        else:
            return None          
        
    def file_path(self, type, version):
        if self.data_file:
            if self.settings:
                if type == "masters" and version == str(set_padding(0,self.project.project_padding)):
                    return self.master
                    
                versions_path = os.path.join(self.settings.current_project_path, self.project.assets_dir,self.catagory_name,self.asset_name,self.component_name,type)
                version_file = "%s_%s_%s.%s"%(self.asset_name,self.component_name,version,"ma") if type == "versions" else "%s_%s_%s_%s.%s"%(self.asset_name,self.component_name,"MASTER",version,"ma")                
                return os.path.join(versions_path, version_file)  
        else:
            return None    
    
    @property
    def versions(self):
        if self.project:
            if self.data_file:
                versions = files.list_directory(self.versions_path,self.project.project_file_type)
                if versions:
                    versions_dict = files.dict_versions(versions,self.project.project_padding)
                    
                    version_nodes = []                 
                    for key in versions_dict:

                        version_nodes.append(VersionNode(key, path = versions_dict[key], author = "autor" ,number = key, date = key, note = "no note", stage = self))

                    return version_nodes

        return None

    @property
    def versiosnModel(self):
        if self.versions:
            return dtm.PipelineVersionsModel(self.versions)
        else:
            print "else"
            return dtm.PipelineVersionsModel(self.emptyVersions)

    @property
    def emptyVersions(self):

        return [NewNode("new...", stage = self)]


    def last_version(self):
        if self.project:
            if self.data_file:
                if self.settings:

                    sorted_versions = self.versions
                    if sorted_versions:
                            return sorted_versions[-1]
                        

                
    def new_version(self):



        if self.project:
            if self.data_file:
                
                versions = self.versions
                versions = self.versions
                if versions:
                    last = versions[-1]
                else:
                    last = 0

                
                version_number = set_padding(last+1,self.project.project_padding)                
      
                file_name = "%s_%s_%s.%s"%(self.asset_name,self.component_name,version_number,"ma")                   
                scene_path = maya.save_scene_as(path = self.versions_path, file_name = file_name ) 
                                
                new_version = {}
                new_version["path"] = scene_path
                new_version["date_created"] = "%s %s"%(time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"))
                new_version["author"] = self.settings.user[0]#"USER"
                new_version["note"] = "No notes"   
                                
                versions = self.versions_  
                versions[version_number] = new_version
                self.versions_ = versions          
    
    
    def delete_version(self, type, version):
        if self.data_file:
            if self.settings:
                versions = self.versions_ if type == "versions" else self.masters_
                if not isinstance(version, list):

                    files.delete(self.file_path(type, version))
                                                                              
                    if version in versions:
                        del versions[version]
                    if type == "versions":    
                        self.versions_ = versions
                    else:
                        self.masters_ = versions 
                    
                else:
                    for v in version:
                        files.delete(self.file_path(type, v))
                        
                        if v in versions:
                            del versions[v]
                        
                    if type == "versions":    
                        self.versions_ = versions
                    else:
                        self.masters_ = versions 
                                        
                return True                                    
        else:
            return None   
    
    @property
    def masters(self):
        if self.project:
            if self.data_file:
                if self.settings:
                   
                    masters = files.list_directory(self.masters_path,self.project.project_file_type)
                    
                    if masters:
                        masters_dict = files.dict_versions(masters,self.project.project_padding)
                        
                        sorted_masters = files.sort_version(masters_dict)
                        return sorted_masters
                    else:
                        return None


    @property
    def master(self):
        if self.project:
            if self.data_file:
                if self.settings:
                    master_name = "%s_%s_%s.%s"%(self.asset_name,self.component_name,"MASTER","ma")
                    
                    master_file = os.path.join(self.stage_path,master_name) 
                    if os.path.isfile(master_file):
                        return master_file
        return None
        
    '''
    @property
    def thumbnail(self):
        if self.project:
            if self.data_file:
                if self.settings:
                    thumbnail_name = os.path.join(self.tumbnails_path,"%s.%s"%(self.component_name,"png"))
                    if os.path.isfile(thumbnail_name):
                        return QtGui.QPixmap(thumbnail_name)
        
        return large_image_icon
    '''
    @property
    def thumbnail(self):
        file = self.thumbnail_path
        if file:
            return QtGui.QPixmap(file)
        
        return large_image_icon

    @property
    def thumbnail_path(self):
        if self.project:
            if self.data_file:
                if self.settings:
                    thumbnail_name = os.path.join(self.tumbnails_path,"%s.%s"%(self.component_name,"png"))
                    if os.path.isfile(thumbnail_name):
                        return thumbnail_name
        
        return None

        
    def new_master(self, from_file = False):
        if self.project:
            if self.data_file:
                if self.settings:
                                    
                    new_master = {}
                    new_master["date_created"] = "%s %s"%(time.strftime("%d/%m/%Y"),time.strftime("%H:%M:%S"))
                    new_master["author"] = self.settings.user[0]
                    new_master["note"] = "No notes"  
                              
                    if self.masters:
                        # master versions existst
                        
                        masters = self.masters
                        last = masters[len(masters)-1]
                        version_number = set_padding(last+1,self.project.project_padding)                
                   
                    else:
                        
                        # this will be the first master
                        version_number = set_padding(1,self.project.project_padding)                
                    
                    maya.clean_up_file()
                    
                    
                    file_name = "%s_%s_%s_%s.%s"%(self.asset_name,self.component_name,"MASTER",version_number,"ma")                                                       
                    if not from_file:                    
                        scene_path = maya.save_scene_as(path = self.masters_path, file_name = file_name )                         
                    else:                      
                        scene_path = os.path.join(self.masters_path,file_name)
                        files.file_copy(from_file, scene_path )
                        
                    new_master["path"] = scene_path    
                    masters = self.masters_ 
                    masters[str(set_padding(0,self.project.project_padding))] = new_master 
                    masters[version_number] = new_master
                    
                    self.masters_ = masters 
                                    
                    master_name = "%s_%s_%s.%s"%(self.asset_name,self.component_name,"MASTER","ma")
                    master_file = os.path.join(self.settings.current_project_path,self.project.assets_dir,self.catagory_name,self.asset_name,self.component_name,master_name) 
                    files.file_copy(scene_path, master_file)

                    maya.open_scene(master_file)
 
                    

    def make_master(self, version):
                
        source = self.file_path("masters",version)

        if source:
            files.file_copy(source, self.master)

            new_master = {}
            new_master["date_created"] = self.date_created("masters",version)
            
            new_master["author"] =  self.author("masters",version)
            new_master["note"] = self.note("masters",version) 

            masters = self.masters_ 
            masters[str(set_padding(0,self.project.project_padding))] = new_master 

            self.masters_ = masters 
            
            return True
        
        return False

    def rename(self, new_name):
         
        #asset_path = os.path.dirname(files.dir_rename(os.path.dirname(self.data_file_path),new_name))
        #componentes = files.list_dir_folders(asset_path)
        #if new_name in componentes:
        #    dlg.massage("critical", "Sorry", "This Component exsists" )
        #    return False
        
        versions = {}
        for version in self.versions:
            version_number = set_padding(version,self.project.project_padding) 
            versions[version] = [self.file_path("versions",version_number), "%s_%s_%s"%(self.asset_name,new_name,version_number)] 
            files.file_rename(versions[version][0],versions[version][1])

        if self.master:
            masters = {}
            for version in self.masters:
                version_number = set_padding(version,self.project.project_padding) 
                masters[version] = [self.file_path("masters",version_number), "%s_%s_%s_%s"%(self.asset_name,new_name,"MASTER",version_number)] 
                files.file_rename(masters[version][0],masters[version][1])

                
            master = [self.master, "%s_%s_%s"%(self.asset_name,new_name,"MASTER")]
            files.file_rename(master[0],master[1])
         
        thumb_path = os.path.join(self.tumbnails_path,"%s.%s"%(self.component_name,"png"))   
        if os.path.isfile(thumb_path):
            files.file_rename(thumb_path,new_name) 

        self.component_name = new_name
        path = files.file_rename(self.data_file_path,new_name)        
        
        stage_path = files.dir_rename(os.path.dirname(self.data_file_path),new_name)  
     
        self.set_data_file(os.path.join(stage_path,"%s.%s"%(new_name,"pipe")))
        self.data_file = self.data_file.read()
        
        return True
        
    def rename_asset(self, new_name):
         
        
        versions = {}
        for version in self.versions:
            version_number = set_padding(version,self.project.project_padding) 
            versions[version] = [self.file_path("versions",version_number), "%s_%s_%s"%(new_name,self.component_name,version_number)] 
            files.file_rename(versions[version][0],versions[version][1])

        if self.master:
            masters = {}
            for version in self.masters:
                version_number = set_padding(version,self.project.project_padding) 
                masters[version] = [self.file_path("masters",version_number), "%s_%s_%s_%s"%(new_name,self.component_name,"MASTER",version_number)] 
                files.file_rename(masters[version][0],masters[version][1])

                
            master = [self.master, "%s_%s_%s"%(new_name,self.component_name,"MASTER")]
            files.file_rename(master[0],master[1])
        
        self.asset_name = new_name       
        return True
                

    def get_data_file(self,path = None):
                
        if path:
            dir = os.path.dirname(path)
            file = os.path.join(dir,"*.pipe")
            
            
            if len(glob.glob(file)) == 1: #if its a master
                return glob.glob(file)[0]                        

            dir = os.path.dirname(dir)
            file = os.path.join(dir,"*.pipe")
                                       
            if len(glob.glob(file)) == 1: #if its a version
                return glob.glob(file)[0]  
            
            return None
            
        return None        

    @property
    def type(self):
        
        if self.component_name:
            return "component"
        
        
        shot = pipeline_shot(path = self.data_file_path, project = self.project, settings = self.settings)

        if shot:
            if shot.shot_name:
                return "shot"
            
        return None    

    def log(self):

        if self.settings:
            self.settings.log()
        
        log.info("logging component '%s' at asset '%s' at catagory '%s'"%(self.component_name,self.asset_name,self.catagory_name))       
        
        log.info("component path %s"%self.stage_path)
                
        [ log.info("  %s"%f) for f in files.list_all(self.stage_path) if isinstance(files.list_all(self.stage_path),list) ]
                               
        log.info("compnnent data file: %s"%self.data_file_path)
        
        log.info(self.data_file.print_nice())

        log.info("end logging component ")    