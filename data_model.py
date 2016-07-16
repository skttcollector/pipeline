
from PySide import QtCore, QtGui, QtXml
import cPickle
import os
import functools

import data as dt
reload(dt)

def set_icons():
    localIconPath = os.path.join(os.path.dirname(__file__), 'icons/treeview/')
    if not os.path.exists(localIconPath):
        return 
    global branch_more
    global branch_closed
    global branch_open
    global branch_end
    global vline
    
    branch_more = os.path.join(localIconPath,"branch-more.svg")
    branch_closed = os.path.join(localIconPath,"branch-closed.svg")
    branch_open = os.path.join(localIconPath,"branch-open.svg")
    branch_end = os.path.join(localIconPath,"branch-end.svg")
    vline = os.path.join(localIconPath,"vline.svg")

    global folder_icon
    global cube_icon
    global cube_icon_full
    global add_icon
    global large_image_icon
    folder_icon = os.path.join(localIconPath, "%s.svg"%"folder")
    cube_icon = os.path.join(localIconPath, "%s.svg"%"cube")    
    cube_icon_full = os.path.join(localIconPath, "%s.svg"%"cube-fill") 
    add_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg"%"add"))
    large_image_icon = QtGui.QPixmap(os.path.join(localIconPath, "%s.svg"%"large_image")) 
                    
    
set_icons()





class PipelineContentsView(QtGui.QTableView):
    def __init__(self,parent = None):
        super(PipelineContentsView, self).__init__(parent)
        
        #display options
        
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection) 
        self.setWordWrap(True)
        self.setShowGrid(False)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)        
        self.icons_size(32)       
        self.setMinimumWidth(250)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSortingEnabled(True)
        self.horizontalHeader().setOffset(10)
        self.verticalHeader().hide()
        
        #local variables
        self._treeView = None        
        self._treeProxyModel = None
        self._treeSourceModel = None
        
        self._treeParent = None
        self._treeParentIndex = None


    @property
    def treeView(self):
        return self._treeView
    
    @treeView.setter
    def treeView(self, view):
        self._treeView = view

    @property
    def treeProxyModel(self):
        if self._treeProxyModel:
            return self._treeProxyModel
        
        return None
    
    @treeProxyModel.setter
    def treeProxyModel(self, model):
        self._treeProxyModel = model        

    @property
    def treeSourceModel(self):
        if self._treeSourceModel:
            return self._treeSourceModel
            
        return None
    
    @treeSourceModel.setter
    def treeSourceModel(self, model):
        self._treeSourceModel = model   

    def init_treeView(self):
        self.treeProxyModel = self.treeView.model()
        self.treeSourceModel = self.treeProxyModel.sourceModel()        

    def asTreeIndex(self, index):
        node = self.getNode(index)
        return self.treeSourceModel.indexFromNode(node,self.treeView.rootIndex())

    def icons_size(self, int):
        self.setIconSize(QtCore.QSize(int ,int)  )       
        self.verticalHeader().setDefaultSectionSize(int )
               
    def getNode(self, index):
        return self.model().getNode(index)

    def asTreeModelIndex(self, index):
        return self.treeView.asModelIndex(index)  

    def click(self, index):

        node = self.getNode(index)
        if not node.typeInfo() == "ADD-COMPONENT" and not node.typeInfo() == "ADD-ASSET" and not node.typeInfo() == "ADD-FOLDER":
            treeIndex = self.asTreeIndex(node)
            print treeIndex
    
    '''
    updates the table view with a new model
    the model is a custom table model, bulit from the childs of the selected branch in the treeview
    
    index: QItemSelection
    '''
      
    def update(self, selection):
        #if the selection is not empty
        if len(selection.indexes())>0:
            # using only the first selection for this task
            index = selection.indexes()[0]
             
            if index.isValid():
                '''
                the index is from the tree's proxymodel
                we need to convert it to the source index
                '''
                
                treeModel = self.treeSourceModel
                src = self.asTreeModelIndex(index) 
                node =  self.treeView.asModelNode(src)

                contenetsList = []
    
                self._treeParentIndex = src
                self._treeParent = node
                                
                for row in range(treeModel.rowCount(src)):

                    item_index = treeModel.index(row,0,src)
                    treeNode = treeModel.getNode(item_index) 
                    contenetsList.append(treeNode)
                    
                # ----> this is the section to append 'add' buttons to the list
                #
                #list.append(dt.AddComponent("new"))  
                #if node.typeInfo() == "NODE":                   
                #    list.append(dt.AddAsset("new")) 
                #    list.append(dt.AddFolder("new"))                 
         
                if len(contenetsList) > 0:         
                    self.setModel(PipelineContentsModel(contenetsList))
                
                    # resize the table headers to the new content
                    self.horizontalHeader().setResizeMode(0,QtGui.QHeaderView.Stretch)#ResizeToContents)
                    self.horizontalHeader().setResizeMode(1,QtGui.QHeaderView.Stretch)
                
                    return True
                         
        # in case the selection is empty, or the index was invalid, clear the table            
        self.clearModel()        
        return False
    
    def clearModel(self):
        self.setModel(None)

    def contextMenuEvent(self, event):
     
        handled = True
        node = None
        index = self.indexAt(event.pos())
        menu = QtGui.QMenu()            
        actions = []
        
        if index.isValid():
            
            tableModelNode = self.model().getNode(index)                
            src = self.asTreeIndex(index)                 
            node =  self.treeSourceModel.getNode(src)
                   
        if node:

            if tableModelNode.typeInfo()[0:3] != "ADD":
                
                if node.typeInfo() == "NODE": 
                    actions.append(QtGui.QAction("Delete", menu, triggered = functools.partial(self.delete, src, node) ))

                    
                if node.typeInfo() == "ASSET":
                    actions.append(QtGui.QAction("Delete", menu, triggered = functools.partial(self.delete, src, node) ))

                    
                if node.typeInfo() == "COMPONENT":
                    actions.append(QtGui.QAction("Delete", menu, triggered = functools.partial(self.delete, src, node) ))
                
            else:
                pass
                '''
                ---> this is for if we use the table buttons to add nodes to the tree...
            
                
                if tableModelNode.typeInfo() == "ADD-COMPONENT":
                    actions.append(QtGui.QAction("Create new Component", menu, triggered = functools.partial(self.create_new_component,self._treeParent) ))
                elif tableModelNode.typeInfo() == "ADD-ASSET":
                    actions.append(QtGui.QAction("Create new Asset", menu, triggered = functools.partial(self.create_new_asset,self._treeParent) ))  
                elif tableModelNode.typeInfo() == "ADD-FOLDER":
                    actions.append(QtGui.QAction("Create new folder", menu, triggered = functools.partial(self.create_new_folder,self._treeParent) ))     
                '''
                    
        else:
                       
            actions.append(QtGui.QAction("Create new Component", menu, triggered = functools.partial(self.create_new_component,self._treeParent) ))
            
            if self._treeParent.typeInfo() == "NODE":
            
                actions.append(QtGui.QAction("Create new folder", menu, triggered = functools.partial(self.create_new_folder, self._treeParent) ))
                actions.append(QtGui.QAction("Create new Asset", menu, triggered = functools.partial(self.create_new_asset,self._treeParent) ))
   
        menu.addActions(actions)      
       
        if handled:
            
            menu.exec_(event.globalPos())
            event.accept() #TELL QT IVE HANDLED THIS THING
            
        else:
            event.ignore() #GIVE SOMEONE ELSE A CHANCE TO HANDLE IT
                   
        return

    def delete(self,  index,node):
        self.clearModel()
        self.treeView.delete(index,node)        
        self.treeView.restoreSelection()
        
        idx = self.treeView._model.mapFromSource(self.treeView.userSelection)
        self.update(QtGui.QItemSelection(idx,idx))

    def create_new_folder(self, parent):
        
        self.clearModel()             
        self.treeView.create_new_folder(parent)               
        self.treeView.restoreSelection()
        
        idx = self.treeView._model.mapFromSource(self.treeView.userSelection)
        self.update(QtGui.QItemSelection(idx,idx))

    def create_new_asset(self, parent):
        
        self.clearModel()             
        self.treeView.create_new_asset(parent)              
        self.treeView.restoreSelection()
        
        idx = self.treeView._model.mapFromSource(self.treeView.userSelection)
        self.update(QtGui.QItemSelection(idx,idx))
        
    def create_new_component(self, parent):
        
        self.clearModel()             
        self.treeView.create_new_component(parent)              
        self.treeView.restoreSelection()
        
        idx = self.treeView._model.mapFromSource(self.treeView.userSelection)
        self.update(QtGui.QItemSelection(idx,idx))        


  
                    
class pipelineTreeView(QtGui.QTreeView):
    def __init__(self,parent = None):
        super(pipelineTreeView, self).__init__(parent)
        
        # display options
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setDragEnabled( True )
        self.setAcceptDrops( True )
        self.setDragDropMode( QtGui.QAbstractItemView.InternalMove )
        self.resizeColumnToContents(True) 
                
        #local variables

        self._ignoreExpentions = False
        self._expended_states = None        
        self._userSelection = None       
        self._tableView = None
        self._proxyModel = None
        self._sourceModel = None
        
        #stylesheet 
        self.setStyleSheet('''  
                           
                           QTreeView::item:focus {
                           }
                           QTreeView::branch:has-siblings:!adjoins-item {
                                border-image:url(''' + vline + ''') 0;
                           }
                           
                           QTreeView::branch:has-siblings:adjoins-item {
                                border-image:url(''' + branch_more + ''') 0;
                           }
                           
                           QTreeView::branch:!has-children:!has-siblings:adjoins-item {
                                border-image:url(''' + branch_end + ''') 0;
                           }

                           QTreeView::branch:has-children:!has-siblings:closed,
                           QTreeView::branch:closed:has-children:has-siblings {
                                border-image: none;
                                image:url(''' + branch_closed + ''') 0;
                           }

                           QTreeView::branch:open:has-children:!has-siblings,
                           QTreeView::branch:open:has-children:has-siblings  {
                                border-image: none;
                                image: url(''' + branch_open + ''') 0;
                           }
                           

                           
                            ''')

    

    def setModel(self,model):

        super(pipelineTreeView,self).setModel(model)
        
        self.proxyModel = self.model()
        self.sourceModel = self.proxyModel.sourceModel()        
        
        '''
        this will expend the tree only on the first level, which should be
        the projects name folder
        the rest will be collapsed
        '''
        self.expandAll()
        i =  self.model().index(0,0,self.rootIndex())
        
        for row in range(self.model().rowCount(i)):
            x = self.model().index(row,0,i)
            self.setExpanded(x,False)
        
        
        '''
        save the expended state of the tree
        '''
        self.saveState()


    @property
    def tableView(self):
        return self._tableView
    
    @tableView.setter
    def tableView(self, view):
        self._tableView = view 

    @property
    def proxyModel(self):
        return self._proxyModel
    
    @proxyModel.setter
    def proxyModel(self, model):
        self._proxyModel = model        

    @property
    def sourceModel(self):
        return self._sourceModel
    
    @sourceModel.setter
    def sourceModel(self, model):
        self._sourceModel = model   


    @property
    def userSelection(self):
        return self._userSelection
    
    @userSelection.setter
    def userSelection(self, selection):
        self._userSelection = selection   

    def asProxyIndex(self,index):
        return self.proxyModel.index(0,0,index)

    
    def asModelIndex(self, index):
        return self.proxyModel.mapToSource(index)

    def fromProxyIndex(self, index):
        return self.proxyModel.mapFromSource(index)

    def asModelNode(self, index):
        return self.sourceModel.getNode(index)
        
        
        
    def modelIndexFromNode(self, node):
        return self.sourceModel.indexFromNode(node,self.rootIndex())
    
    def selectRoot(self):
        
        self.setCurrentIndex(self.asProxyIndex(self.rootIndex()))
        self.saveSelection()

    def saveSelection(self):
        
        if len(self.selectedIndexes())>0:
            self.userSelection = self.asModelIndex(self.selectedIndexes()[0])
        
    
    def saveState(self):
        '''
        recursive function to save the expention state fo the tree to a dictionary
        '''
    
        if self._ignoreExpentions == True:
            return  
                        
        def rec( dict, mdl, index):
            
            for row in range(mdl.rowCount(index)):
                 
                   
                i = mdl.index(row,0, index)
                node = mdl.data(i, 165)
                
                if self.isExpanded(i):
                    dict[node] = True
                else:
                    dict[node] = False  
                      
                rec(dict, mdl, i)     
                   
        self._expended_states = {}
        rec(self._expended_states,self.proxyModel,self.rootIndex())

        
    def restoreState(self):    
        '''
        recursive function to restore the expention state fo the tree to a dictionary
        '''
        def rec(  mdl, index):
            
            for row in range(mdl.rowCount(index)):
                 
                   
                i = mdl.index(row,0, index)
                node = mdl.data(i, 165)
                
                if self._expended_states[node] == True:
                    self.setExpanded(i, True)

                     
                rec( mdl, i)     
                            
        self.collapseAll()
        rec(self.proxyModel,self.rootIndex())                
        self.restoreSelection()

    def restoreSelection(self):

        index = self.fromProxyIndex(self.userSelection)
        self.selectionModel().select(index, QtGui.QItemSelectionModel.ClearAndSelect)

        
    def dropEvent(self, event):
        super(pipelineTreeView,self).dropEvent(event)
        #QTreeView.dropEvent(self, evt)
        if not event.isAccepted():
            # qdnd_win.cpp has weird behavior -- even if the event isn't accepted
            # by target widget, it sets accept() to true, which causes the executed
            # action to be reported as "move", which causes the view to remove the
            # source rows even though the target widget didn't like the drop.
            # Maybe it's better for the model to check drop-okay-ness during the
            # drag rather than only on drop; but the check involves not-insignificant work.
            event.setDropAction(QtCore.Qt.IgnoreAction)
                
        # this was required when i misused the insert rows function of the model...
        #self._proxyModel.invalidate()

   
    def contextMenuEvent(self, event):
        
        handled = True
        index = self.indexAt(event.pos())
        menu = QtGui.QMenu()        
        node = None

        
        if index.isValid():
            src = self.asModelIndex(index)
            node = self.asModelNode(src)

        actions = []  
          
        if node:

            if node.typeInfo() == "NODE": 
                actions.append(QtGui.QAction("Create new Asset", menu, triggered = functools.partial(self.create_new_asset, src) ))
                actions.append(QtGui.QAction("Create new Folder", menu, triggered = functools.partial(self.create_new_folder, src) ))
                actions.append(QtGui.QAction("Delete", menu, triggered = functools.partial(self.delete, src) ))
                
            elif node.typeInfo() == "ASSET":

                actions.append(QtGui.QAction("Delete", menu, triggered = functools.partial(self.delete, src) ))
                

        else:
            actions.append(QtGui.QAction("Create new folder", menu, triggered = functools.partial(self.create_new_folder,QtCore.QModelIndex()) ))
            actions.append(QtGui.QAction("Create new Asset", menu, triggered = functools.partial(self.create_new_asset,QtCore.QModelIndex()) ))

        menu.addActions(actions)      

        if handled:

            menu.exec_(event.globalPos())
            event.accept() #TELL QT IVE HANDLED THIS THING
            
        else:
            event.ignore() #GIVE SOMEONE ELSE A CHANCE TO HANDLE IT
                   
        return

    '''
    functions to add/remove tree nodes
    this is we will want some user input...
    
    '''
    def delete(self,  index):
        # clear the table view              
        self.tableView.update(QtGui.QItemSelection())
        
        node = self.asModelNode(index)
        parentIndex = self.sourceModel.parent(index)
        self.sourceModel.removeRows(node.row(),1,parentIndex, kill=True)
        
        return True
    def create_new_folder(self, parent):
        node = dt.Node("folder")        
        self.sourceModel.insertRows( 1, 1, parent = parent , node = node)
        
    def create_new_asset(self, parent):
        node = dt.AssetNode("asset","")
        self._sourceModel.insertRows( 1, 1, parent = parent , node = node)

    def create_new_component(self, parent):
        node = dt.ComponentNode("component","")
        self._sourceModel.insertRows( 1, 1, parent = parent , node = node)





class PipelineProjectModel(QtCore.QAbstractItemModel):
    
    
    sortRole   = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1
    expendedRole = QtCore.Qt.UserRole + 2
    
    """INPUTS: Node, QObject"""
    def __init__(self, root, parent=None):
        super(PipelineProjectModel, self).__init__(parent)
        self._rootNode = root
        self._tempIndex = None

    def staticIndex(self, index):
        return QtCore.QPersistentModelIndex(index)

        
    @property
    def rootNode(self):
        return self._rootNode

    """INPUTS: QModelIndex"""
    """OUTPUT: int"""
    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    """INPUTS: QModelIndex"""
    """OUTPUT: int"""
    def columnCount(self, parent):
        return 1
    

    
    """INPUTS: QModelIndex, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def data(self, index, role):
        
        if not index.isValid():
            return None

        node = index.internalPointer()


        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
           
            return node.data(index.column())
 
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                resource = node.resource()
                return QtGui.QIcon(QtGui.QPixmap(resource))
            
        if role == SceneGraphModel.sortRole:
            return node.typeInfo()

        if role == SceneGraphModel.filterRole:
            return node.typeInfo()

        if role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(0,19)
        
        # this is for expending state - the result must be uniqe!!!
        if role == 165:
            return node.id
        
        if role == SceneGraphModel.expendedRole:

            return self.isExpended(index)
               
        #if role == QtCore.Qt.FontRole:
         #  if node.typeInfo() == "COMPONENT":
          #     boldFont = QtGui.QFont()
           #    boldFont.setBold(True)
            #   return boldFont

    """INPUTS: QModelIndex, QVariant, int (flag)"""
    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if index.isValid():
            
            node = index.internalPointer()
            
            if role == QtCore.Qt.EditRole:
                node.setData(index.column(), value)
                self.dataChanged.emit(index, index)
            if role == SceneGraphModel.expendedRole:
                node.expendedState(self.isExpended(index))
                self.dataChanged.emit(index, index)               
                return True
            
        return False

    
    """INPUTS: int, Qt::Orientation, int"""
    """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Project"
            else:
                return "Type"

    """INPUTS: QModelIndex"""
    """OUTPUT: int (flag)"""

            
    
    """INPUTS: QModelIndex"""
    """OUTPUT: int (flag)"""
    def flags(self, index):
        
        if not index.isValid():

            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled 

        if index.isValid():
            node = self.getNode(index)
            
            if node.typeInfo() == "ROOT":
                return  QtCore.Qt.ItemIsEnabled |QtCore.Qt.ItemIsSelectable
            
            if node.typeInfo() == "COMPONENT":
                return  QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
    
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable    
    
    """INPUTS: QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return the parent of the node with the given QModelIndex"""
    def parent(self, index):
        
        node = self.getNode(index)
        parentNode = node.parent()
        
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        
        return self.createIndex(parentNode.row(), 0, parentNode)
        
    """INPUTS: int, int, QModelIndex"""
    """OUTPUT: QModelIndex"""
    """Should return a QModelIndex that corresponds to the given row, column and parent node"""
    
    
    def index( self, row, column, parentIndex ):
        
        if not self.hasIndex( row, column, parentIndex ):
            return    QtCore.QModelIndex() 
             
        parent = self.getNode( parentIndex )
        return  self.createIndex( row, column, parent.child( row ) ) 
    


    """CUSTOM"""
    """INPUTS: QModelIndex"""
    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
            
        return self._rootNode

    
    """INPUTS: int, int, QModelIndex"""
    def insertRows(self, position, rows, parent=QtCore.QModelIndex(), node = None):
        parentNode = self.getNode(parent)

        self.beginInsertRows(parent, position, position + rows - 1)
        
        
        for row in range(rows):
            
            childCount = parentNode.childCount()
            childNode = node
            success = parentNode.insertChild(position, childNode)
            print success
        
        self.endInsertRows()
        return True


    def removeRows( self, row, count, parentIndex, **kwargs ):

        '''Remove a number of rows from the model at the given row and parent.'''
        self.beginRemoveRows( parentIndex, row, row+count-1 )
        parent = self.getNode( parentIndex )
        for x in range( count ):
            
            # remove rows is being called in every drop action,
            # we need to know if the remove is with the intention to actually delete the data in the nodes
            
            if "kill" in kwargs:
                if kwargs["kill"] == True:            
                    parent.child(row).delete()
                    
                    
            parent.removeChild( row )
        self.endRemoveRows()
        self.dataChanged.emit( parentIndex, parentIndex )
        return True

    def supportedDropActions( self ):

        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction
     

    def mimeData( self, indices ):
        '''Encode serialized data from the item at the given index into a QMimeData object.'''
        
        data = ''

        parent_index =  self.parent(indices[0])
        item = self.getNode( indices[0] )
        self._tempIndex = indices[0]
        try:
            data += cPickle.dumps( item )

        except:
            pass

        mimedata = QtCore.QMimeData()
        mimedata.setData( 'application/x-qabstractitemmodeldatalist', data ) 
   
        return mimedata
     
    def dropMimeData( self, mimedata, action, row, column, parentIndex ):
        '''Handles the dropping of an item onto the model.
         
        De-serializes the data into a TreeItem instance and inserts it into the model.
        '''
        if not mimedata.hasFormat( 'application/x-qabstractitemmodeldatalist' ):
            return False
            
        item = cPickle.loads( str( mimedata.data( 'application/x-qabstractitemmodeldatalist' ) ) )
        dropParent = self.getNode( parentIndex )
        
        # do not allow a folder to be dropped on an asset...
        if dropParent.typeInfo() == "ASSET":
            if item.typeInfo() == "NODE" or item.typeInfo() == "ASSET":
                return False
        
        if dropParent.typeInfo() == "ROOT":
            return False
            
               
        #dropParent.addChild( item )
        self.insertRows( dropParent.childCount(), 1, parent = parentIndex , node = item)
            
        self.dataChanged.emit( parentIndex, parentIndex )
         
        return True 
       

    def indexFromNode(self, node, rootIndex):
        '''
        recursive function to get Index from a node,
        we use a unique node id to do this
        the id is stored as a UserRole int 165
        
        '''                
        def rec(d, index):
            
            for row in range(self.rowCount(index)):
                 
                   
                i = self.index(row,0, index)
                id = self.data(i, 165)
                if id == node.id:
                    d.append(i)
                else:
                    pass
                          
                rec(d, i)     
            
        
        data = []
        rec(data, rootIndex)
        if len(data)>0:
            return data[0]
        else:
            # if the node is not in the tree return an empty index
            return QtCore.QModelIndex()


class PipelineContentsModel(QtCore.QAbstractTableModel):
    
    def __init__(self, components = [], parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.__components = components


    def headerData(self, section, orientation, role):

        if role == QtCore.Qt.DisplayRole:
            
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return "Contents"
                if section == 1:
                    return "Info"
            else:
                return 

        if role == QtCore.Qt.DecorationRole:

            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return QtGui.QIcon(QtGui.QPixmap(cube_icon))
                if section == 1:
                    return QtGui.QIcon(QtGui.QPixmap(cube_icon))
            else:
                return 


    def rowCount(self, parent):
        return len(self.__components)

    def columnCount(self, parent):
        return 1
        
    def data(self, index, role):
        
        
        if role == QtCore.Qt.EditRole:
            return self.__components[index.row()].name
        
        
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                resource = self.__components[index.row()].resource()
                return QtGui.QIcon(QtGui.QPixmap(resource))
              
        if role == QtCore.Qt.DisplayRole:
            
            row = index.row()
            if index.column() == 0:
                return self.__components[row].name
            if index.column() == 1:
                return "test test test test test test"

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        
    """CUSTOM"""
    """INPUTS: QModelIndex"""
    def getNode(self, index):
        if index.isValid():
            return self.__components[index.row()]

        return None        
        
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            
            row = index.row()
            
            if role == QtCore.Qt.EditRole:
                self.__components[row].name = value 
                self.dataChanged.emit(index, index)
             
                return True

            
        return False

    #=====================================================#
    #INSERTING & REMOVING
    #=====================================================#
    def insertRows(self, position, rows, parent = QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)

        self.endInsertRows()
        
        return True
   
    def removeRows(self, position, rows, parent = QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        
        for i in range(rows):
            value = self.__components[position]
            self.__components.remove(value)
             
        self.endRemoveRows()
        return True

class PipelineProjectProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self,parent = None):
        
        super(PipelineProjectProxyModel, self).__init__(parent)
        self._treeView = None
        
    @property
    def treeView(self):
        if self._treeView:
            return self._treeView
        else:
            return None
            
    @treeView.setter
    def treeView(self, object):
        self._treeView = object
                    
    def filterAcceptsRow(self,sourceRow,sourceParent):

        # hide components from the treeview
        id =  self.sourceModel().index(sourceRow,0,sourceParent)    

        if super(PipelineProjectProxyModel,self).filterAcceptsRow(sourceRow,sourceParent): 
            
            if self.sourceModel().getNode(id).typeInfo() == "COMPONENT":
                return False
                      
            return True
        
        return self.hasAcceptedChildren(sourceRow,sourceParent)

    def hasAcceptedChildren(self,sourceRow,sourceParent):

        model=self.sourceModel()
        sourceIndex=model.index(sourceRow,0,sourceParent)
        if not sourceIndex.isValid():
            return False
        indexes=model.rowCount(sourceIndex)
        for i in range(indexes):
            if self.filterAcceptsRow(i,sourceIndex):
                return True
        
        return False

    def setFilterRegExp(self, exp):
             
        super(PipelineProjectProxyModel, self).setFilterRegExp(exp)
        if self.treeView:
            if len(exp)>0:  
                #self.treeView._ignoreSelections = True
                      
                self.treeView._ignoreExpentions = True
                self.treeView.expandAll()
                self.treeView._ignoreExpentions = False
            else:
                self.treeView._ignoreExpentions = True
                self.treeView.restoreState()          
                self.treeView._ignoreExpentions = False         

        