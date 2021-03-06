import numpy as np
import scipy.sparse as sp
import torch
from torch.utils.data import Dataset


def load_graph(dataset, k):
    if k:
        path = 'data/{}{}_graph.txt'.format(dataset, k)
    else:
        path = 'data/{}_graph.txt'.format(dataset)
    print('Loading {} dataset from {}...'.format(dataset, path))

    data = np.loadtxt('data/{}.txt'.format(dataset))
    n, _ = data.shape
    labels = np.loadtxt('data/{}_label.txt'.format(dataset), dtype=int)
    if dataset in ['cite', 'pubmed', 'hhar']:
        labels = labels - 1    # hhar and pubmed, cite

    idx = np.array([i for i in range(n)], dtype=np.int32)
    idx_map = {j: i for i, j in enumerate(idx)}
    edges_unordered = np.genfromtxt(path, dtype=np.int32)
    if dataset == 'pubmed':
        edges_unordered = edges_unordered - 1    # # only for lfr and pubmed

    edges = np.array(list(map(idx_map.get, edges_unordered.flatten())),
                     dtype=np.int32).reshape(edges_unordered.shape)
    adj = sp.coo_matrix((np.ones(edges.shape[0]), (edges[:, 0], edges[:, 1])),
                        shape=(n, n), dtype=np.float32)

    # build symmetric adjacency matrix
    adj = adj + adj.T.multiply(adj.T > adj) - adj.multiply(adj.T > adj)
    adj = adj + sp.eye(adj.shape[0])
    adj = normalize(adj)
    adj = sparse_mx_to_torch_sparse_tensor(adj)

    return adj, data, labels


def normalize(mx):
    """Row-normalize sparse matrix"""
    rowsum = np.array(mx.sum(1))
    r_inv = np.power(rowsum, -1).flatten()
    r_inv[np.isinf(r_inv)] = 0.
    r_mat_inv = sp.diags(r_inv)
    mx = r_mat_inv.dot(mx)
    return mx


def sparse_mx_to_torch_sparse_tensor(sparse_mx):
    """Convert a scipy sparse matrix to a torch sparse tensor."""
    sparse_mx = sparse_mx.tocoo().astype(np.float32)
    indices = torch.from_numpy(
        np.vstack((sparse_mx.row, sparse_mx.col)).astype(np.int64))
    values = torch.from_numpy(sparse_mx.data)
    shape = torch.Size(sparse_mx.shape)
    return torch.sparse.FloatTensor(indices, values, shape)

