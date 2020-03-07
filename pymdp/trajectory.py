import copy
import numpy as np
import os

class Trajectory:
    def __init__(self):
        self.nodes = []
        self.value = 0.0
        self.active = True
    
    def is_active(self):
        return self.active

    def update_node(self, node, value):
        self.nodes.append(node)
        self.value = value

    def display(self):
        for node in self.nodes:
            print(str(node), end = ' ')
        print('Score = ', self.value)

    
class TrajStation:
    def __init__(self):
        self.trajs = [[Trajectory()]]
        self.features = []
        self.feat_valid = []
        self.level = 0
    
    def get_trajs_by_level(self, level):
        if len(self.trajs) == level:
            self.trajs.append([])
        return self.trajs[level]
    
    def get_trajs_current(self):
        return self.trajs[self.level]

    def get_trajs_previous(self):
        return self.trajs[self.level -1]
    
    def add_node(self, _from, _to, _val):
        trajs = self.get_trajs_previous()
        new_traj = copy.deepcopy(trajs[_from])
        new_traj.update_node(_to, _val)
        self.trajs[-1].append(new_traj)

    def move_to_next_level(self):
        self.level += 1
        if len(self.trajs) <= self.level:
            self.trajs.append([])
    
    def move_to_previous_level(self):
        self.level -=1

    def add_feature(self, feat, feat_valid):
        self.features.append(feat)
        self.feat_valid.append(feat_valid)

    def display(self):
        trajs = self.get_trajs_current()
        for i in range(len(trajs)):
            print('Traj ', i, ' : ')
            trajs[i].display()

    def prepare_data(self, folder):
        # first, sort all trajectories
        all_trajs = [x for sublist in self.trajs for x in sublist]
        #all_trajs = np.concatenate(self.trajs) #self.data_all.sort(key=lambda x: float(x[5]), reverse=False)
        all_trajs.sort(key=lambda x : x.value, reverse=False)
        adjacent_matrices = []
        print('length of features = ', len(self.features))
        for i in range(len(self.features)):
            adjacent_matrices.append(np.zeros((self.feat_valid[i], self.feat_valid[i]), dtype=bool))
        
        for traj in all_trajs:
            print("score = ", str(traj.value))
            for i in range(len(traj.nodes)):
                k = traj.nodes[i]
                m = adjacent_matrices[i]
                m[k, :] = True
                m[:, k] = False
                print(i, k)

        if len(adjacent_matrices) == 0:
            return
        
        if os.path.exists(folder) is False:
            os.makedirs(folder)
        
        for i in range(len(adjacent_matrices)):
            rows, cols = np.where(adjacent_matrices[i] == True)
            ind = np.array([rows, cols])
            np.save(folder +'/adj-'+str(i)+'.py', ind)

        for i in range(len(self.features)):
            np.save(folder+'/feat-' + str(i) + '.npy', self.features[i])
    
    def export_best_segmentation(self, folder, export_polys):
        all_trajs = [x for sublist in self.trajs for x in sublist]
        best_traj = max(all_trajs, key=lambda x : x.value)
        print('val: ', best_traj.value)
        
        for i in range(len(best_traj.nodes)):
            k = best_traj.nodes[i]
            print("node: ", k)
            if i == len(best_traj.nodes) - 1:
                with open(os.path.join(folder, 'result-'+str(i+1)+'.off'), 'w') as f:
                    f.write(export_polys[i][k][0])

            with open(os.path.join(folder, 'result-'+str(i)+'.off'), 'w') as f:
                f.write(export_polys[i][k][1])
        
        print(len(export_polys))

        if os.path.exists(folder) is False:
            os.makedirs(folder)