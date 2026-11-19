
### Verify, noise 0, ignoring mnar, N=300/group, bad_source=0.4
| metric | branch | missing | missing+graded | missing+found | fix (missing+graded+found) |
|---|---|---|---|---|---|
| none secure (worst weekly) | 0.003 | 0.003 | 0.000 | 0.003 | 0.003 |
| none ever secure in-chat | 0.007 | 0.010 | 0.000 | 0.037 | 0.023 |
| gamer secure (worst weekly) | 0.150 | 0.217 | 0.150 | 0.300 | 0.257 |
| gamer secure w3-10 | 0.102 | 0.150 | 0.100 | 0.219 | 0.171 |
| partial secure w3-10 | 0.053 | 0.084 | 0.057 | 0.227 | 0.193 |
| strong secure w3-10 | 0.699 | 0.758 | 0.713 | 0.918 | 0.913 |
| AUC none-strong w8 | 0.974 | 0.985 | 0.986 | 1.000 | 1.000 |
| AUC gamer-strong w8 | 0.912 | 0.914 | 0.921 | 0.959 | 0.968 |
| strong median days to secure | 9.698 | 8.752 | 10.750 | 5.868 | 6.813 |

### Verify, noise sym10, ignoring mnar, N=300/group, bad_source=0.4
| metric | branch | missing | missing+graded | missing+found | fix (missing+graded+found) |
|---|---|---|---|---|---|
| none secure (worst weekly) | 0.003 | 0.003 | 0.000 | 0.007 | 0.003 |
| none ever secure in-chat | 0.020 | 0.030 | 0.000 | 0.053 | 0.027 |
| gamer secure (worst weekly) | 0.093 | 0.153 | 0.097 | 0.233 | 0.183 |
| gamer secure w3-10 | 0.065 | 0.103 | 0.063 | 0.156 | 0.113 |
| partial secure w3-10 | 0.051 | 0.064 | 0.047 | 0.181 | 0.155 |
| strong secure w3-10 | 0.485 | 0.550 | 0.488 | 0.800 | 0.770 |
| AUC none-strong w8 | 0.918 | 0.947 | 0.935 | 0.998 | 0.997 |
| AUC gamer-strong w8 | 0.845 | 0.856 | 0.851 | 0.935 | 0.935 |
| strong median days to secure | 11.831 | 10.875 | 14.721 | 6.874 | 7.866 |

### Verify, noise sym20, ignoring mnar, N=300/group, bad_source=0.4
| metric | branch | missing | missing+graded | missing+found | fix (missing+graded+found) |
|---|---|---|---|---|---|
| none secure (worst weekly) | 0.003 | 0.003 | 0.000 | 0.010 | 0.007 |
| none ever secure in-chat | 0.043 | 0.050 | 0.023 | 0.087 | 0.057 |
| gamer secure (worst weekly) | 0.057 | 0.080 | 0.053 | 0.140 | 0.120 |
| gamer secure w3-10 | 0.038 | 0.058 | 0.033 | 0.103 | 0.075 |
| partial secure w3-10 | 0.034 | 0.045 | 0.025 | 0.150 | 0.110 |
| strong secure w3-10 | 0.302 | 0.350 | 0.279 | 0.627 | 0.581 |
| AUC none-strong w8 | 0.848 | 0.876 | 0.865 | 0.968 | 0.968 |
| AUC gamer-strong w8 | 0.764 | 0.770 | 0.771 | 0.877 | 0.878 |
| strong median days to secure | 15.745 | 14.861 | 22.733 | 9.854 | 12.747 |

### Verify, noise len20, ignoring mnar, N=300/group, bad_source=0.4
| metric | branch | missing | missing+graded | missing+found | fix (missing+graded+found) |
|---|---|---|---|---|---|
| none secure (worst weekly) | 0.003 | 0.010 | 0.003 | 0.020 | 0.017 |
| none ever secure in-chat | 0.073 | 0.097 | 0.027 | 0.153 | 0.083 |
| gamer secure (worst weekly) | 0.260 | 0.347 | 0.283 | 0.497 | 0.403 |
| gamer secure w3-10 | 0.163 | 0.233 | 0.173 | 0.331 | 0.262 |
| partial secure w3-10 | 0.142 | 0.188 | 0.144 | 0.331 | 0.299 |
| strong secure w3-10 | 0.651 | 0.710 | 0.667 | 0.878 | 0.863 |
| AUC none-strong w8 | 0.978 | 0.987 | 0.988 | 0.996 | 0.996 |
| AUC gamer-strong w8 | 0.861 | 0.848 | 0.863 | 0.907 | 0.923 |
| strong median days to secure | 7.866 | 7.781 | 10.822 | 6.733 | 6.850 |

### Verify, noise 0, ignoring mcar, N=300/group, bad_source=0.4
| metric | branch | missing | missing+graded | missing+found | fix (missing+graded+found) |
|---|---|---|---|---|---|
| none secure (worst weekly) | 0.007 | 0.010 | 0.003 | 0.010 | 0.007 |
| none ever secure in-chat | 0.017 | 0.020 | 0.003 | 0.040 | 0.030 |
| gamer secure (worst weekly) | 0.150 | 0.217 | 0.150 | 0.300 | 0.257 |
| gamer secure w3-10 | 0.102 | 0.150 | 0.100 | 0.219 | 0.171 |
| partial secure w3-10 | 0.053 | 0.084 | 0.057 | 0.227 | 0.193 |
| strong secure w3-10 | 0.557 | 0.688 | 0.642 | 0.867 | 0.863 |
| AUC none-strong w8 | 0.939 | 0.981 | 0.981 | 1.000 | 1.000 |
| AUC gamer-strong w8 | 0.841 | 0.889 | 0.898 | 0.940 | 0.952 |
| strong median days to secure | 11.758 | 9.826 | 11.819 | 6.877 | 7.798 |

### Verify, noise sym10, ignoring mcar, N=300/group, bad_source=0.4
| metric | branch | missing | missing+graded | missing+found | fix (missing+graded+found) |
|---|---|---|---|---|---|
| none secure (worst weekly) | 0.007 | 0.010 | 0.003 | 0.013 | 0.010 |
| none ever secure in-chat | 0.047 | 0.050 | 0.010 | 0.097 | 0.057 |
| gamer secure (worst weekly) | 0.093 | 0.153 | 0.097 | 0.233 | 0.183 |
| gamer secure w3-10 | 0.065 | 0.103 | 0.063 | 0.156 | 0.113 |
| partial secure w3-10 | 0.051 | 0.064 | 0.047 | 0.181 | 0.155 |
| strong secure w3-10 | 0.367 | 0.486 | 0.433 | 0.730 | 0.703 |
| AUC none-strong w8 | 0.859 | 0.929 | 0.919 | 0.987 | 0.985 |
| AUC gamer-strong w8 | 0.758 | 0.817 | 0.821 | 0.902 | 0.908 |
| strong median days to secure | 13.797 | 11.836 | 15.796 | 8.711 | 9.842 |

### Verify, noise sym20, ignoring mcar, N=300/group, bad_source=0.4
| metric | branch | missing | missing+graded | missing+found | fix (missing+graded+found) |
|---|---|---|---|---|---|
| none secure (worst weekly) | 0.003 | 0.003 | 0.003 | 0.013 | 0.013 |
| none ever secure in-chat | 0.060 | 0.067 | 0.030 | 0.143 | 0.103 |
| gamer secure (worst weekly) | 0.057 | 0.080 | 0.053 | 0.140 | 0.120 |
| gamer secure w3-10 | 0.038 | 0.058 | 0.033 | 0.103 | 0.075 |
| partial secure w3-10 | 0.034 | 0.045 | 0.025 | 0.150 | 0.110 |
| strong secure w3-10 | 0.221 | 0.295 | 0.244 | 0.536 | 0.502 |
| AUC none-strong w8 | 0.789 | 0.852 | 0.845 | 0.954 | 0.953 |
| AUC gamer-strong w8 | 0.679 | 0.731 | 0.739 | 0.844 | 0.848 |
| strong median days to secure | 20.805 | 18.677 | 29.865 | 11.831 | 15.683 |

### Verify, noise len20, ignoring mcar, N=300/group, bad_source=0.4
| metric | branch | missing | missing+graded | missing+found | fix (missing+graded+found) |
|---|---|---|---|---|---|
| none secure (worst weekly) | 0.007 | 0.013 | 0.007 | 0.030 | 0.023 |
| none ever secure in-chat | 0.107 | 0.123 | 0.060 | 0.237 | 0.167 |
| gamer secure (worst weekly) | 0.260 | 0.347 | 0.283 | 0.497 | 0.403 |
| gamer secure w3-10 | 0.163 | 0.233 | 0.173 | 0.331 | 0.262 |
| partial secure w3-10 | 0.142 | 0.188 | 0.144 | 0.331 | 0.299 |
| strong secure w3-10 | 0.524 | 0.649 | 0.599 | 0.817 | 0.802 |
| AUC none-strong w8 | 0.933 | 0.978 | 0.980 | 0.991 | 0.991 |
| AUC gamer-strong w8 | 0.771 | 0.814 | 0.828 | 0.870 | 0.895 |
| strong median days to secure | 10.759 | 9.671 | 11.836 | 7.679 | 8.688 |

written /home/vishnu/edux26-research/docs/research/overnight/sims/fixes/results/verify_sim_n300_bad0.4.json
