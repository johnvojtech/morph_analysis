all: train_supervised train_semisuper train_small train_auto
train_supervised:
	python -m bi_lstm_crf corpora/stats_corpus --model_dir=models/supervised  --batch_size=512 --num_epoch=5 --save_best_val_model
	python -m bi_lstm_crf corpora/finetune_corpus --model_dir=models/supervised  --batch_size=64 --num_epoch=100 --recovery --save_best_val_model

train_semisuper:
	python -m bi_lstm_crf corpora/stats_corpus --model_dir=models/semi-supervised --batch_size=512 --num_epoch=5 --save_best_val_model
	python -m bi_lstm_crf corpora/finetune_corpus --model_dir=models/semi-supervised --batch_size=64 --num_epoch=100 --recovery --save_best_val_model

train_small:
	python -m bi_lstm_crf corpora/finetune_corpus --model_dir=models/small --batch_size=64 --num_epoch=100 --save_best_val_model

train_auto:
	python -m bi_lstm_crf corpora/stats_full_aut_corpus --model_dir=models/auto --batch_size=512 --num_epoch=5 --save_best_val_model
	python -m bi_lstm_crf corpora/finetune_corpus --model_dir=models/auto --batch_size=64 --num_epoch=100 --recovery --save_best_val_model

train_auto_super:
	 python -m bi_lstm_crf corpora/stats_aut_corpus --model_dir=models/auto_dev --batch_size=512 --num_epoch=5 --save_best_val_model
	 python -m bi_lstm_crf corpora/finetune_corpus --model_dir=models/auto_dev --batch_size=64 --num_epoch=100 --recovery --save_best_val_model

train_auto_3:
	python -m bi_lstm_crf corpora/stats_restr_corpus --model_dir=models/auto_restr --batch_size=512 --num_epoch=5 --save_best_val_model
	python -m bi_lstm_crf corpora/finetune_corpus --model_dir=models/auto_restr --batch_size=64 --num_epoch=100 --recovery --save_best_val_model

predict_all:
	python crf_tagger.py models/small test_t.tsv > test_small.tsv
	python crf_tagger.py models/semi-supervised test_t.tsv > test_semi.tsv
	python crf_tagger.py models/supervised test_t.tsv > test_super.tsv

predict_auto:
	 python crf_tagger.py models/auto test_t.tsv > test_auto.tsv

predict_auto_2:
	python crf_tagger.py models/auto_dev test_t.tsv > test_auto_dev.tsv

predict_auto_3:
	python crf_tagger.py models/auto_restr test_t.tsv > test_auto_restr.tsv

